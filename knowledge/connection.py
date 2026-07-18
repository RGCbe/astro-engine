"""Neo4j connection helper for Astro-KG.
Reads NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD from the environment,
falling back to the workspace root's `.env` or standard defaults.
"""
import os
from pathlib import Path
from neo4j import GraphDatabase


def _load_dotenv() -> None:
    """Minimal .env loader so python-dotenv is not required."""
    # Look for .env in the parent directory (workspace root)
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        # Fall back to checking setup-finder's or trading-bot's .env if they exist
        for alt_path in ["setup-finder/.env", "trading-bot/.env"]:
            p = Path(__file__).resolve().parent.parent / alt_path
            if p.exists():
                env_path = p
                break
    
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def get_driver():
    _load_dotenv()
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "neo4j")
    return GraphDatabase.driver(uri, auth=(user, password))
