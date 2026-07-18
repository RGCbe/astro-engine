import urllib.request, json

queries = {
    "liber astronomiae bonatti": "Liber_Astronomiae_Bonatti.pdf",
    "jataka desh marga vedic astrology": "Jataka_Desh_Marga.pdf",
    "firmicus maternus matheseos astrology": "Matheseos_Firmicus_Maternus.pdf",
    "dhruva nadi satyacharya astrology": "Dhruva_Nadi_Satyacharya.pdf",
    "di tian sui bazi chinese astrology": "Di_Tian_Sui_BaZi.pdf",
}

for q, target in queries.items():
    url = "https://archive.org/advancedsearch.php?q=" + urllib.request.quote(q)
    url += "&fl[]=identifier&fl[]=title&rows=5&output=json&mediatype=texts"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            docs = data.get("response", {}).get("docs", [])
            print(f"\nQ: {q}")
            for d in docs:
                print(f"  ID: {d['identifier']} | Title: {d.get('title','?')}")
    except Exception as e:
        print(f"Q: {q} -> Error: {e}")
