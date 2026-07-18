#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deep_v1 verbatim extraction - resume incomplete gemma_extractions/*_deep.json.

Keys via api-vault HTTP (VAULT_TOKEN) or in-process unlock on VPS (--vault-direct).
Never prints or writes full API keys.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ROOT / "Books"
GEMMA = ROOT / "gemma_extractions"
PAUSE_FLAG = ROOT / "scratch" / "EXTRACTION_PAUSED.flag"


def _extraction_paused() -> bool:
    return PAUSE_FLAG.is_file()

PROVIDER_CHAIN = ("google", "cerebras", "groq", "nvidia", "sambanova")
SKIP_QUOTA_STATES = frozenset({"exhausted", "error_model"})
EXTRACTOR_TAG = "deep_v1 (verbatim, anti-censor, page-chunked)"

SYSTEM_PROMPT = """You extract verbatim classical Vedic astrology rules from OCR text.
Do NOT censor, soften, or omit content about death, disease, poverty, sexuality, or misfortune.
Extract every predictive rule, sutra, definition, yoga, and technique in the chunk.

Return ONLY valid JSON (no markdown fences):
{"rules": [{"original_text": "...", "english_translation": "...", "sanskrit_iast": "",
"verse_id": "BOOK.chapter.verse or empty string", "categories": ["tag", ...],
"involves_planets": ["Sun", ...], "involves_houses": [], "involves_signs": ["Aries", ...],
"type": "rule|sutra|definition|yoga|technique|table|general"}]}

Preserve OCR wording in original_text; english_translation may clarify OCR errors.
Use empty lists where unknown. verse_id may use ? for uncertain verse numbers."""

PLANETS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
SIGNS = {
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
}


def _smart_chunks(text: str, target_chars: int = 2500) -> Iterator[tuple[int, str]]:
    """Paragraph-aware chunking; falls back to line-aware when no blank lines."""
    if text.count("\n\n") < 2:
        lines = text.split("\n")
        buf, idx = "", 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if buf and len(buf) + len(line) + 1 > target_chars:
                yield idx, buf
                idx += 1
                buf = line
            else:
                buf = (buf + "\n" + line).strip() if buf else line
        if buf:
            yield idx, buf
        return

    paras = text.split("\n\n")
    buf, idx = "", 0
    for p in paras:
        p = p.strip()
        if not p:
            continue
        if buf and len(buf) + len(p) + 2 > target_chars:
            yield idx, buf
            idx += 1
            buf = p
        else:
            buf = (buf + "\n\n" + p).strip() if buf else p
    if buf:
        yield idx, buf


def _guess_verse_ids(text: str) -> list[str]:
    """Light verse/chapter references for provenance hints."""
    ids: list[str] = []
    for m in re.finditer(
        r"(?:Chapter|Ch\.?)\s*(\d+)[,\s]+(?:verse|v\.?)\s*(\d+)",
        text,
        re.I,
    ):
        ids.append(f"{m.group(1)}.{m.group(2)}")
    for m in re.finditer(r"\b(\d{1,3})\.(\d{1,3})\b", text):
        ids.append(f"{m.group(1)}.{m.group(2)}")
    return list(dict.fromkeys(ids))[:20]


def _chunk_count(text: str, target_chars: int) -> int:
    return len(list(_smart_chunks(text, target_chars)))


def resolve_target_chars(
    text: str,
    data: dict,
    *,
    override: int | None = None,
) -> int:
    """Pick chunk size consistent with meta total or a finished smaller split (stale meta)."""
    if override is not None:
        return int(override)
    stored = data.get("target_chars")
    if stored:
        return int(stored)

    last_done = int(data.get("last_chunk_processed", -1))
    n_meta = int(data.get("n_chunks_total") or 0)

    if n_meta > 0:
        tc_meta = calibrate_target_chars(text, n_meta)
        n_sim = _chunk_count(text, tc_meta)
        if abs(n_sim - n_meta) <= 5:
            print(f"  meta split: tc={tc_meta} n_chunks={n_sim} (meta={n_meta})")
            return tc_meta

    # Inflated meta (e.g. 505) but all text processed under a smaller split (373 chunks).
    if last_done >= 0 and n_meta > last_done + 5:
        for tc in range(400, 12000, 25):
            n = _chunk_count(text, tc)
            if n == last_done + 1 and n < n_meta - 10:
                print(
                    f"  stale meta: using finished split tc={tc} n_chunks={n} "
                    f"(meta={n_meta}, last_done={last_done})"
                )
                return tc

    return calibrate_target_chars(text, n_meta or 2500)


def calibrate_target_chars(text: str, n_chunks_total: int) -> int:
    """Find target_chars so _smart_chunks count ~= n_chunks_total (fine search)."""
    if n_chunks_total <= 0:
        return 2500

    def _count(tc: int) -> int:
        return len(list(_smart_chunks(text, tc)))

    best_tc, best_n = 2500, _count(2500)
    best_delta = abs(best_n - n_chunks_total)
    for tc in range(400, 12000, 50):
        n = _count(tc)
        delta = abs(n - n_chunks_total)
        if delta < best_delta:
            best_tc, best_n, best_delta = tc, n, delta
    # Refine around best coarse match
    for tc in range(max(400, best_tc - 250), best_tc + 251, 25):
        n = _count(tc)
        delta = abs(n - n_chunks_total)
        if delta < best_delta:
            best_tc, best_n, best_delta = tc, n, delta
    return best_tc


class VaultKeyPool:
    """Checkout keys from vault HTTP API or direct key_manager (VPS only)."""

    def __init__(self, service: str, use_direct: bool = False):
        self.service = service
        self.use_direct = use_direct
        self._session = None
        self._km = None
        self.vault_url = os.environ.get("VAULT_URL", "http://127.0.0.1:5055").rstrip("/")
        self.vault_token = os.environ.get("VAULT_TOKEN", "")

    def _ensure_direct(self) -> None:
        if self._km is not None:
            return
        vault_root = os.environ.get("VAULT_ROOT", "/root/api-expense-manager")
        env_file = Path(vault_root) / ".env"
        if env_file.exists() and not os.environ.get("VAULT_MASTER_PASSWORD"):
            for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if line.startswith("VAULT_MASTER_PASSWORD="):
                    os.environ["VAULT_MASTER_PASSWORD"] = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
        if vault_root not in sys.path:
            sys.path.insert(0, vault_root)
        os.chdir(vault_root)
        import config  # noqa: WPS433
        import crypto  # noqa: WPS433
        import models  # noqa: WPS433
        import key_manager  # noqa: WPS433

        models.init_db()
        salt_hex = models.get_meta("vault_salt")
        pwd = config.VAULT_MASTER_PASSWORD or os.environ.get("VAULT_MASTER_PASSWORD", "")
        if not pwd or not salt_hex:
            raise RuntimeError("Direct vault: set VAULT_MASTER_PASSWORD on VPS")
        crypto.unlock_vault(pwd, bytes.fromhex(salt_hex))
        if not crypto.is_vault_unlocked():
            raise RuntimeError("Direct vault unlock failed")
        self._km = key_manager
        self._service_id = os.environ.get("VAULT_SERVICE_ID", "93c4070a")
        print("vault: in-process unlock OK")

    def checkout(self, provider: str) -> dict | None:
        if self.use_direct:
            self._ensure_direct()
            aliases = {
                "google": ("google", "gemini"),
                "gemini": ("google", "gemini"),
            }
            for prov in aliases.get(provider, (provider,)):
                hit = self._km.checkout_key(self._service_id, prov)
                if hit:
                    return hit
            return None

        import requests

        if self._session is None:
            self._session = requests.Session()
            self._session.headers["Authorization"] = f"Bearer {self.vault_token}"
            self._session.headers["Content-Type"] = "application/json"

        if not self.vault_token:
            return None
        try:
            r = self._session.post(
                f"{self.vault_url}/api/v1/keys/checkout",
                json={"service": self.service, "provider": provider},
                timeout=15,
            )
            if r.status_code == 200:
                return r.json()
            return None
        except Exception as exc:
            print(f"vault HTTP checkout failed: {exc}")
            return None

    def report_usage(
        self,
        lease_id: str,
        *,
        success: bool,
        tokens_prompt: int = 0,
        tokens_completion: int = 0,
        error_type: str = "",
        latency_ms: int = 0,
        caller: str = "",
    ) -> None:
        if self.use_direct and self._km:
            try:
                self._km.report_usage(
                    lease_id,
                    tokens_prompt=tokens_prompt,
                    tokens_completion=tokens_completion,
                    success=success,
                    error_type=error_type,
                    latency_ms=latency_ms,
                    caller=caller,
                )
            except Exception:
                pass
            return
        if not self.vault_token or not lease_id or self._session is None:
            return
        try:
            self._session.post(
                f"{self.vault_url}/api/v1/usage/report",
                json={
                    "lease_id": lease_id,
                    "tokens_prompt": tokens_prompt,
                    "tokens_completion": tokens_completion,
                    "success": success,
                    "error_type": error_type,
                    "latency_ms": latency_ms,
                    "caller": caller,
                },
                timeout=5,
            )
        except Exception:
            pass


def _quota_state(q: dict) -> str:
    status = q.get("status", "unknown")
    if status == "rate_limited":
        return "exhausted"
    if status == "error":
        err = (q.get("error") or "").lower()
        if "404" in err or "not found" in err:
            return "error_model"
        if "429" in err:
            return "exhausted"
        return "error"
    rpm_rem = int(q.get("rpm_remaining") or 0)
    rpd_rem = int(q.get("rpd_remaining") or 0)
    tpd_rem = int(q.get("tpd_remaining") or 0)
    if rpm_rem == 0 and int(q.get("rpm_limit") or 0) > 0:
        return "exhausted"
    if rpd_rem == 0 and int(q.get("rpd_limit") or 0) > 0:
        return "exhausted"
    if tpd_rem == 0 and int(q.get("tpd_limit") or 0) > 0:
        return "exhausted"
    day_pct = float(q.get("day_usage_pct") or 0)
    if day_pct >= 95:
        return "near_limit"
    if rpm_rem > 0 and int(q.get("rpm_limit") or 0) > 0:
        if rpm_rem <= max(2, int(q["rpm_limit"]) * 0.1):
            return "near_limit"
    return "OK"


def provider_chain_with_quota(pool: VaultKeyPool) -> tuple[str, ...]:
    """Skip exhausted / bad-model providers when vault-direct quota check is available."""
    if not pool.use_direct:
        return PROVIDER_CHAIN
    try:
        pool._ensure_direct()
        import crypto  # noqa: WPS433
        import models  # noqa: WPS433
        import quota_checker  # noqa: WPS433
        keys_with_secrets = []
        for k in models.get_all_keys():
            if k["status"] != "active":
                continue
            prov = k["provider"]
            if prov not in PROVIDER_CHAIN and prov not in ("gemini",):
                continue
            dec = crypto.decrypt_secret(k["api_key_encrypted"])
            if dec:
                k["api_key_decrypted"] = dec
                keys_with_secrets.append(k)
        quotas = quota_checker.check_all_quotas(keys_with_secrets)
        by_prov: dict[str, str] = {}
        for k in keys_with_secrets:
            by_prov.setdefault(k["provider"] if k["provider"] != "gemini" else "google", "OK")
        for q in quotas:
            for k in keys_with_secrets:
                if k["id"] == q.get("key_id"):
                    prov = k["provider"]
                    if prov == "gemini":
                        prov = "google"
                    by_prov[prov] = _quota_state(q)
                    break
        chain = []
        for prov in PROVIDER_CHAIN:
            state = by_prov.get(prov, "OK")
            if state in SKIP_QUOTA_STATES:
                print(f"  skip {prov}: quota {state}")
                continue
            if state == "near_limit":
                print(f"  warn {prov}: near limit (will try)")
            chain.append(prov)
        if chain:
            print(f"  provider chain: {', '.join(chain)}")
            return tuple(chain)
    except Exception as exc:
        print(f"  quota prefetch skipped: {exc}")
    return PROVIDER_CHAIN


def _parse_rules_json(raw: str) -> list[dict]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", raw)
        if not m:
            return []
        data = json.loads(m.group(0))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("rules") or data.get("items") or []
    return []


def _normalize_rule(rule: dict, book: str, chunk_idx: int, extractor: str) -> dict | None:
    if not isinstance(rule, dict):
        return None
    orig = (rule.get("original_text") or rule.get("trigger") or "").strip()
    if len(orig) < 12:
        return None
    eng = (rule.get("english_translation") or orig).strip()
    cats = rule.get("categories") or []
    if isinstance(cats, str):
        cats = [cats]
    planets = [p for p in (rule.get("involves_planets") or []) if p in PLANETS]
    signs = [s for s in (rule.get("involves_signs") or []) if s in SIGNS]
    houses = rule.get("involves_houses") or []
    if not isinstance(houses, list):
        houses = []
    return {
        "original_text": orig,
        "sanskrit_iast": (rule.get("sanskrit_iast") or "").strip(),
        "english_translation": eng,
        "verse_id": (rule.get("verse_id") or "").strip(),
        "categories": [str(c) for c in cats if c],
        "involves_planets": planets,
        "involves_houses": houses,
        "involves_signs": signs,
        "type": (rule.get("type") or "rule").strip(),
        "_book": book,
        "_chunk_idx": chunk_idx,
        "_extractor": extractor,
    }


def llm_extract_chunk(
    pool: VaultKeyPool,
    book: str,
    chunk_idx: int,
    n_total: int,
    chunk_text: str,
    *,
    max_tokens: int = 8000,
    temperature: float = 0.1,
) -> tuple[list[dict], str]:
    from openai import OpenAI

    user = (
        f"Book: {book}\nChunk {chunk_idx + 1} of {n_total}\n"
        f"Hint verse refs in chunk: {_guess_verse_ids(chunk_text)}\n\n"
        f"TEXT:\n{chunk_text[:120000]}"
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
    last_err: Exception | None = None
    chain = provider_chain_with_quota(pool)
    for prov in chain:
        key = pool.checkout(prov)
        if not key:
            print(f"  no key for {prov}")
            continue
        api_key = key.get("api_key", "")
        tail = f"...{api_key[-4:]}" if len(api_key) >= 4 else "????"
        print(f"  trying {prov} model={key.get('model')} key={tail}")
        label = prov if prov != "google" else "gemini-3-flash"
        start = time.time()
        try:
            client = OpenAI(api_key=api_key, base_url=key.get("base_url"))
            resp = client.chat.completions.create(
                model=key.get("model"),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            text = (resp.choices[0].message.content or "").strip()
            latency = int((time.time() - start) * 1000)
            tp = getattr(resp.usage, "prompt_tokens", 0) if resp.usage else 0
            tc = getattr(resp.usage, "completion_tokens", 0) if resp.usage else 0
            pool.report_usage(
                key.get("lease_id", ""),
                success=True,
                tokens_prompt=tp,
                tokens_completion=tc,
                latency_ms=latency,
                caller=f"astro.deep_extract.{book}",
            )
            rules = _parse_rules_json(text)
            out = []
            for r in rules:
                norm = _normalize_rule(r, book, chunk_idx, label)
                if norm:
                    out.append(norm)
            if out:
                return out, label
            last_err = RuntimeError("empty rules parsed")
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            err_s = str(e)
            is_rl = "429" in err_s or "rate_limit" in err_s.lower()
            is_404 = "404" in err_s or "not found" in err_s.lower()
            if prov == "cerebras" and is_404:
                print(f"  skip cerebras for rest of run (model 404)")
            pool.report_usage(
                key.get("lease_id", ""),
                success=False,
                error_type="rate_limit" if is_rl else "error",
                latency_ms=latency,
                caller=f"astro.deep_extract.{book}",
            )
            print(f"  chunk {chunk_idx} {prov} FAIL: {err_s[:120]}")
            last_err = e
    if last_err:
        raise last_err
    raise RuntimeError("All vault providers failed or returned no rules")


def resume_book(
    book: str,
    *,
    max_chunks: int | None = None,
    target_chars: int | None = None,
    vault_service: str = "astro",
    vault_direct: bool = False,
) -> dict:
    src = BOOKS / f"{book}_extracted.txt"
    out_path = GEMMA / f"{book}_deep.json"
    if not src.exists():
        raise FileNotFoundError(src)
    if not out_path.exists():
        raise FileNotFoundError(out_path)

    text = src.read_text(encoding="utf-8", errors="replace")
    data = json.loads(out_path.read_text(encoding="utf-8", errors="replace"))
    n_total_meta = int(data.get("n_chunks_total") or 0)
    last_done = int(data.get("last_chunk_processed", -1))
    tc = resolve_target_chars(text, data, override=target_chars)
    chunks = list(_smart_chunks(text, tc))
    sim_n = len(chunks)

    # Full text already processed under this split but stale meta total (e.g. 505 vs 373).
    if sim_n > 0 and last_done >= sim_n - 1:
        if not data.get("is_complete") or n_total_meta != sim_n:
            print(
                f"  RECONCILE: processed through chunk {last_done} but "
                f"meta n_total={n_total_meta} -> sim={sim_n} (tc={tc}); marking complete"
            )
            data["n_chunks_total"] = sim_n
            data["target_chars"] = tc
            data["last_chunk_processed"] = sim_n - 1
            data["is_complete"] = True
            out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "book": book,
            "reconciled": True,
            "chunks_done": data.get("last_chunk_processed"),
            "n_chunks_total": sim_n,
            "n_rules_total": data.get("n_rules_total"),
            "is_complete": True,
        }

    n_total = n_total_meta or sim_n
    if sim_n and abs(sim_n - n_total) > 2:
        print(f"  WARN chunk count sim={sim_n} meta={n_total} (resume uses sim={sim_n}, tc={tc})")
        n_total = sim_n

    start_idx = last_done + 1
    end_idx = n_total
    if max_chunks is not None:
        end_idx = min(end_idx, start_idx + max_chunks)

    pool = VaultKeyPool(vault_service, use_direct=vault_direct)
    if not vault_direct and not pool.vault_token:
        raise RuntimeError(
            "Set VAULT_TOKEN for HTTP checkout, or pass --vault-direct on VPS with VAULT_MASTER_PASSWORD"
        )

    if _extraction_paused():
        print(f"EXTRACTION PAUSED ({PAUSE_FLAG.read_text(encoding='utf-8').strip()}). Exiting.")
        return {
            "book": book,
            "paused": True,
            "chunks_done": data.get("last_chunk_processed"),
            "n_chunks_total": n_total,
        }

    print(f"=== {book} resume chunks {start_idx}..{end_idx - 1} (tc={tc}, sim={len(chunks)}) ===")
    added = 0
    for idx in range(start_idx, end_idx):
        if _extraction_paused():
            print(f"EXTRACTION PAUSED at chunk {idx}. Saving progress and exiting.")
            break
        if idx >= len(chunks):
            print(f"  STOP: chunk index {idx} beyond simulated chunks ({len(chunks)})")
            break
        _, chunk_text = chunks[idx]
        t0 = time.time()
        try:
            rules, prov = llm_extract_chunk(pool, book, idx, n_total, chunk_text)
        except (json.JSONDecodeError, RuntimeError) as exc:
            if not isinstance(exc, json.JSONDecodeError) and "JSON" not in str(exc):
                raise
            print(f"  WARN chunk {idx} JSON parse fail ({exc}); skipping chunk")
            data["last_chunk_processed"] = idx
            data["target_chars"] = tc
            data["extracted_at"] = datetime.utcnow().isoformat()
            out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            time.sleep(1.5)
            continue
        dt = time.time() - t0
        data["rules"].extend(rules)
        data["last_chunk_processed"] = idx
        data["n_rules_total"] = len(data["rules"])
        data["target_chars"] = tc
        data["extracted_at"] = datetime.utcnow().isoformat()
        data["is_complete"] = idx >= n_total - 1
        added += len(rules)
        print(f"  [{book}] chunk {idx}/{n_total - 1} OK via {prov} ({dt:.1f}s, +{len(rules)} rules)")
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(1.5)

    return {
        "book": book,
        "chunks_done": data.get("last_chunk_processed"),
        "n_chunks_total": n_total,
        "rules_added": added,
        "n_rules_total": data.get("n_rules_total"),
        "is_complete": data.get("is_complete"),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Resume deep_v1 corpus extraction via vault")
    ap.add_argument("--book", required=True)
    ap.add_argument("--resume", action="store_true", help="Continue from last_chunk_processed")
    ap.add_argument("--max-chunks", type=int, default=None, help="Limit chunks this run")
    ap.add_argument("--target-chars", type=int, default=None)
    ap.add_argument("--vault-service", default=os.environ.get("VAULT_SERVICE", "astro"))
    ap.add_argument(
        "--vault-direct",
        action="store_true",
        help="Use key_manager on VPS (VAULT_MASTER_PASSWORD); no HTTP token",
    )
    args = ap.parse_args()
    if not args.resume:
        print("Use --resume to continue an existing *_deep.json")
        sys.exit(1)
    stats = resume_book(
        args.book,
        max_chunks=args.max_chunks,
        target_chars=args.target_chars,
        vault_service=args.vault_service,
        vault_direct=args.vault_direct,
    )
    print("DONE", json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
