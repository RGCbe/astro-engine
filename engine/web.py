"""
Flask web UI for the astro engine.

Routes:
    GET  /         — birth-data form
    POST /chart    — compute chart, return HTML page with SVG + reading + forecast
    GET  /api/chart?date=...&time=...&place=...&tz=...&lang=en
                   — JSON API: full chart + forecasts + (optional) synthesis

Usage:
    /opt/astro/venv/bin/python -m engine.web              # dev: 0.0.0.0:5000
    /opt/astro/venv/bin/python -m engine.web --port 8080
"""
from __future__ import annotations

import datetime as dt
import json

from flask import Flask, request, render_template_string, jsonify

from engine.chart import compute_chart
from engine.chart_render import render_north, render_south
from engine.forecast import forecast_summary
from engine.i18n import LANGUAGES, translate, localize_chart
from engine.lal_kitab import lal_kitab_chart, chart_summary as lk_summary
from engine.reading import generate_reading

app = Flask(__name__)


FORM_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Astro Engine — birth chart + truth-calibrated forecast</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 720px; margin: 2em auto; padding: 0 1em; }
  h1 { color: #4a3; }
  form > div { margin: 0.6em 0; }
  label { display: inline-block; width: 100px; }
  input, select { padding: 0.4em; font-size: 1em; }
  button { padding: 0.6em 1.2em; font-size: 1em; background: #4a3; color: white; border: none; cursor: pointer; }
  .truth { background: #fffbe6; border-left: 4px solid #d99; padding: 0.7em; margin: 1em 0; font-size: 0.9em; }
</style>
</head>
<body>
<h1>Astro Engine</h1>
<p>Empirically calibrated Vedic chart + forecast. Bayesian-honest, no flattery.</p>
<div class="truth">
  <strong>Truth directive:</strong> this engine reports both bad and good signals. No softening.
  Forecasts include likelihood ratios from a 299-event empirical backtest. Events with weak
  signal will be labeled as such or omitted.
</div>
<form method="POST" action="/chart">
  <div><label>Name:</label><input name="name" placeholder="(optional)" size="30"></div>
  <div><label>Date:</label><input name="date" type="date" required></div>
  <div><label>Time:</label><input name="time" type="time" required></div>
  <div><label>Place:</label><input name="place" placeholder="e.g. Coimbatore" required></div>
  <div><label>Timezone:</label>
    <input name="tz" type="number" step="0.25" value="5.5" required>
    <small>(hours offset from UTC, e.g. 5.5 for IST, -5 for EST)</small>
  </div>
  <div><label>Language:</label>
    <select name="lang">
      <option value="en">English</option>
      <option value="sa">Sanskrit (IAST)</option>
      <option value="hi">Hindi (Devanagari)</option>
      <option value="ta">Tamil</option>
    </select>
  </div>
  <div><label>Chart style:</label>
    <select name="style">
      <option value="south">South Indian (grid)</option>
      <option value="north">North Indian (diamond)</option>
    </select>
  </div>
  <div><label>LLM synthesis:</label>
    <input type="checkbox" name="synth" value="1">
    <small>(slower, ~10s; uses Cerebras API)</small>
  </div>
  <div><button type="submit">Compute chart</button></div>
</form>
<p style="margin-top:2em; color: #888; font-size:0.85em;">
  Engine v0.6 · 110+ tests · cross-validated against PyJHora at lagna Δ=0.000°
  · 61 known charts · 299 documented events. <a href="/api/health">/api/health</a> ·
  source: <a href="https://github.com/" style="color:#888">(local repo)</a>
</p>
</body></html>"""


RESULT_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Chart for {{ name or "(unnamed)" }} — Astro Engine</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 1280px; margin: 1em auto; padding: 0 1em; line-height: 1.55; color: #222; }
  h1, h2, h3 { color: #4a3; }
  .truth { background: #fffbe6; border-left: 4px solid #d99; padding: 0.7em; margin: 1em 0; font-size: 0.85em; }
  .mission { background:#eef7ee; border-left:4px solid #4a3; padding:0.6em; margin:1em 0; font-size:0.85em; }
  .top { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; align-items: start; margin-bottom: 2em; }
  .symm { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; align-items: start; }
  .col-bad { background: #fff5f5; border: 1px solid #fcc; border-radius: 8px; padding: 1em; }
  .col-good { background: #f5fff5; border: 1px solid #cfc; border-radius: 8px; padding: 1em; }
  .chart-svg { background: #fafafa; padding: 1em; border-radius: 8px; text-align:center; }
  pre { background: #f4f4f4; padding: 0.8em; overflow-x: auto; font-size: 0.82em; max-height: 600px; overflow-y: auto; }
  .CRITICAL { color: #b00; font-weight: bold; }
  .HIGH { color: #d33; font-weight: bold; }
  .MODERATE { color: #c80; font-weight: bold; }
  .LOW { color: #888; }
  .SUPREME { color: #285; font-weight: bold; }
  .STRONG  { color: #4a3; font-weight: bold; }
  .LATENT  { color: #999; }
  .item { margin-bottom: 0.6em; padding-bottom: 0.4em; border-bottom: 1px dotted #ccc; font-size: 0.9em; }
  .item small { color: #777; }
  .remedy { background: #fffaf0; border-left: 3px solid #d80; padding: 0.4em 0.6em; margin: 0.3em 0; font-size: 0.85em; border-radius: 4px; }
  .activation { background: #f0faff; border-left: 3px solid #4ab; padding: 0.4em 0.6em; margin: 0.3em 0; font-size: 0.85em; border-radius: 4px; }
  table { border-collapse: collapse; width: 100%; font-size: 0.9em; margin: 0.5em 0; }
  th, td { border: 1px solid #ddd; padding: 0.4em 0.6em; text-align: left; }
  th { background: #efe; }
  .nav { margin: 1em 0; }
  .badge { display:inline-block; padding:1px 6px; border-radius: 3px; font-size:0.75em; font-weight:bold; }
  .badge-bad  { background:#fcc; color:#900; }
  .badge-good { background:#cfc; color:#070; }
  .counts { font-size: 1.1em; margin-bottom: 1em; }
</style>
</head>
<body>
<div class="nav"><a href="/">← New chart</a></div>
<h1>{{ name or "(unnamed)" }} — {{ birth }} ({{ place }})</h1>

<div class="mission">
<strong>Engine mission:</strong> find the bad better than any astrology, find the good with equal rigor, give concrete remedies for the bad, give concrete activations for the good. Both sides reported equally.
</div>

<div class="counts">
  <span class="badge badge-bad">{{ n_afflictions }} afflictions detected</span>
  &nbsp;
  <span class="badge badge-good">{{ n_blessings }} blessings detected</span>
</div>

<div class="top">
  <div>
    <h3>D1 Chart</h3>
    <div class="chart-svg">{{ chart_svg | safe }}</div>
  </div>
  <div>
    <h3>Key facts</h3>
    <table>
      <tr><td>Lagna</td><td>{{ lagna_sign }} {{ lagna_lon }}°</td></tr>
      <tr><td>Lagna lord</td><td>{{ lagna_lord }}</td></tr>
      <tr><td>Moon sign</td><td>{{ moon_sign }}</td></tr>
      <tr><td>Janma nakshatra</td><td>{{ janma_nak }}</td></tr>
      <tr><td>Current MD</td><td>{{ current_md }} (ends {{ current_md_end }})</td></tr>
      <tr><td>Current AD</td><td>{{ current_ad }}</td></tr>
    </table>
    {% if rins %}
    <h3>Lal Kitab karmic debts</h3>
    <ul>{% for r in rins %}<li><strong>{{ r.rin }}</strong> — {{ r.english }}<br><small>{{ r.evidence }}</small></li>{% endfor %}</ul>
    {% endif %}
  </div>
</div>

<div class="symm">
  <div class="col-bad">
    <h2>⚠️ AFFLICTIONS (the bad)</h2>
    {% if afflictions %}
    {% for a in afflictions %}
      <div class="item">
        <span class="{{ a.severity }}">[{{ a.severity }}]</span>
        <strong>{{ a.name }}</strong><br>
        {{ a.description }}<br>
        <small><em>Evidence:</em> {{ a.evidence }} · <em>Source:</em> {{ a.source }}</small>
      </div>
    {% endfor %}
    {% else %}
    <p><em>No major afflictions detected.</em></p>
    {% endif %}

    <h3>🔧 Remedies (paired)</h3>
    {% for entry in remedy_plan %}
      <div class="remedy">
        <strong>{{ entry.affliction.name }}</strong>
        {% for r in entry.remedies %}
          <br>· <strong>{{ r.type }}</strong>: {{ r.action }}{% if r.when %} <small>({{ r.when }})</small>{% endif %}{% if r.caveat %} <em style="color:#a00">{{ r.caveat }}</em>{% endif %}
        {% endfor %}
      </div>
    {% endfor %}
  </div>

  <div class="col-good">
    <h2>✨ BLESSINGS (the good)</h2>
    {% if blessings %}
    {% for b in blessings %}
      <div class="item">
        <span class="{{ b.strength }}">[{{ b.strength }}]</span>
        <strong>{{ b.name }}</strong><br>
        {{ b.description }}<br>
        <small><em>Evidence:</em> {{ b.evidence }} · <em>Source:</em> {{ b.source }}</small>
        {% if b.activation %}
        <div class="activation"><strong>Activation:</strong> {{ b.activation }}</div>
        {% endif %}
      </div>
    {% endfor %}
    {% else %}
    <p><em>No major blessings detected.</em></p>
    {% endif %}
  </div>
</div>

<h2>📅 Calibrated forecasts — next 24 months (ALL events, no skipping)</h2>
{% if forecasts_any %}
<table>
  <tr><th>Event</th><th>Valence</th><th>Best window</th><th>Ensemble LR</th><th>Reliability</th></tr>
  {% for evt, ws in forecasts.items() %}
    {% if ws %}
    <tr>
      <td>{{ evt }}</td>
      <td>{{ ws[0].valence }}</td>
      <td>{{ ws[0].moment }}</td>
      <td>{{ ws[0].ensemble_LR }}</td>
      <td>{{ ws[0].reliability }}</td>
    </tr>
    {% endif %}
  {% endfor %}
</table>
{% endif %}

{% if synthesis_text %}
<h2>📝 LLM-synthesized reading ({{ synthesis_provider }})</h2>
<div style="background:#f8f8f8; padding:1em; border-radius:6px; white-space:pre-wrap; font-size:0.92em;">{{ synthesis_text }}</div>
{% endif %}

<details>
<summary><h3 style="display:inline-block">Full reading markdown (drill-down)</h3></summary>
<pre>{{ reading_md }}</pre>
</details>

</body></html>"""


@app.route("/")
def index():
    return FORM_HTML


@app.route("/chart", methods=["POST"])
def chart():
    f = request.form
    name = f.get("name", "")
    date = f.get("date")
    time = f.get("time")
    place = f.get("place")
    tz = float(f.get("tz", 5.5))
    lang = f.get("lang", "en")
    style = f.get("style", "south")
    do_synth = bool(f.get("synth"))

    try:
        c = compute_chart(name=name, date=date, time=time, tz_hours=tz, place=place)
    except Exception as e:
        return f"<h1>Error</h1><p>{e}</p><p><a href='/'>back</a></p>", 400

    # SVG
    if style == "north":
        svg = render_north(c, lang=lang)
    else:
        svg = render_south(c, lang=lang)

    # Forecast windows
    fc = forecast_summary(c, months_ahead=24)
    forecasts = {}
    for evt, data in fc["forecasts"].items():
        if isinstance(data, list) and data:
            forecasts[evt] = data
    forecasts_any = bool(forecasts)

    # Reading markdown
    reading = generate_reading(c).to_markdown()

    # Lal Kitab
    lk = lal_kitab_chart(dict(c.positions))
    lk_data = lk_summary(lk)

    # Afflictions + Blessings + Remedy plan
    from engine.afflictions import detect_all as detect_afflictions
    from engine.blessings import detect_all as detect_blessings
    from engine.remedies import remedies_for_chart
    afflictions_list = [
        {"code": a.code, "name": a.name, "severity": a.severity,
         "category": a.category, "evidence": a.evidence,
         "source": a.classical_source, "description": a.description}
        for a in detect_afflictions(c)
    ]
    blessings_list = [
        {"code": b.code, "name": b.name, "strength": b.strength,
         "category": b.category, "evidence": b.evidence,
         "source": b.classical_source, "description": b.description,
         "activation": b.activation}
        for b in detect_blessings(c)
    ]
    remedy_plan = remedies_for_chart(c)["afflictions_with_remedies"]

    # Optional LLM synthesis
    synthesis_text = ""
    synthesis_provider = ""
    if do_synth:
        from engine.synthesis import generate_synthesized_reading
        result = generate_synthesized_reading(c, language=lang, max_tokens=2500)
        synthesis_text = result.get("text", "")
        synthesis_provider = result.get("provider_used", "failed")

    return render_template_string(
        RESULT_HTML,
        name=name,
        birth=str(c.birth_dt),
        place=c.place,
        chart_svg=svg,
        lagna_sign=translate("sign", c.lagna_sign, lang) if lang != "en" else c.lagna_sign,
        lagna_lon=round(c.lagna_lon, 2),
        lagna_lord=translate("graha", c.lagna_lord, lang) if lang != "en" else c.lagna_lord,
        moon_sign=translate("sign", c.nakshatras["Moon"]["sign"], lang) if lang != "en" else c.nakshatras["Moon"]["sign"],
        janma_nak=translate("nakshatra", c.lagna_nakshatra, lang) if lang != "en" else c.lagna_nakshatra,
        current_md=translate("graha", c.current_md, lang) if lang != "en" else c.current_md,
        current_md_end=c.current_md_end,
        current_ad=translate("graha", c.current_ad, lang) if lang != "en" else c.current_ad,
        afflictions=afflictions_list,
        blessings=blessings_list,
        remedy_plan=remedy_plan,
        n_afflictions=len(afflictions_list),
        n_blessings=len(blessings_list),
        rins=lk_data["karmic_debts"],
        forecasts=forecasts,
        forecasts_any=forecasts_any,
        reading_md=reading,
        synthesis_text=synthesis_text,
        synthesis_provider=synthesis_provider,
    )


@app.route("/api/chart", methods=["GET"])
def api_chart():
    args = request.args
    try:
        c = compute_chart(
            name=args.get("name", ""),
            date=args.get("date"),
            time=args.get("time"),
            tz_hours=float(args.get("tz", 5.5)),
            place=args.get("place"),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    out = c.summary()
    out["forecast"] = forecast_summary(c, months_ahead=24)

    if args.get("synth", "").lower() in ("1", "true", "yes"):
        from engine.synthesis import generate_synthesized_reading
        out["synthesis"] = generate_synthesized_reading(c, language=args.get("lang", "en"))

    lang = args.get("lang", "en")
    if lang != "en":
        out = localize_chart(out, lang)
    return jsonify(out)


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "engine_version": "0.6",
        "languages": LANGUAGES,
        "truth_directive": "enforced — engine reports both bad and good without softening",
    })


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=5000)
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
