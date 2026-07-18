import re

filepath = "f:/astro/runtime/generate_report.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Insert build_truth_report_section before def generate
func_code = """
def build_truth_report_section(chart):
    from reportlab.platypus import HRFlowable
    from reportlab.lib.enums import TA_CENTER
    flow = []
    tr = chart.get("truth_report")
    if not tr:
        return flow
    
    flow.append(PageBreak())
    flow.append(to_para("KNOWLEDGE-GRAPH TRUTH REPORT", h1))
    flow.append(to_para("Evidence-based synthesis & traceability audit", h1_sub))
    flow.append(HRFlowable(width="100%", thickness=0.8, color=GOLD, spaceAfter=8))
    
    # Metadata summary table
    state = tr.get("report_state", "unknown").upper()
    g_sum = tr.get("graph_summary", {})
    nodes = g_sum.get("nodes", 0)
    edges = g_sum.get("edges", 0)
    claims_count = g_sum.get("claims", 0)
    
    meta_rows = [
        [Paragraph("<b>Report State:</b>", body_small), Paragraph(state, body_small),
         Paragraph("<b>Graph Size:</b>", body_small), Paragraph(f"{nodes} nodes, {edges} edges", body_small)],
        [Paragraph("<b>Verification Level:</b>", body_small), Paragraph("Corpus Cross-Reference (Traceable)", body_small),
         Paragraph("<b>Active Claims:</b>", body_small), Paragraph(str(claims_count), body_small)]
    ]
    t_meta = Table(meta_rows, colWidths=[3.2*cm, 3.8*cm, 3.2*cm, 3.8*cm])
    t_meta.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, GREY_LT),
        ("BACKGROUND", (0,0), (-1,-1), SHEET_BG),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    flow.append(t_meta)
    flow.append(Spacer(1, 0.4*cm))
    
    # 1. Chart Facts
    flow.append(to_para("<b>Calculated Chart Facts (Reproducible):</b>", h2))
    facts = tr.get("chart_facts", [])
    if facts:
        for f in facts:
            lbl = f.get("label", "")
            flow.append(to_para(f"&nbsp;&bull; {lbl}", body))
    else:
        flow.append(to_para("No facts registered in the graph.", body))
    flow.append(Spacer(1, 0.4*cm))
    
    # 2. Active Claims
    flow.append(to_para("<b>Synthesized Claims & Evidence Trails:</b>", h2))
    claims = tr.get("claims", [])
    if claims:
        for c in claims:
            topic = c.get("topic", "").replace("_", " ").upper()
            status = c.get("status", "").upper()
            band = c.get("confidence_band", "").upper()
            statement = c.get("statement", "")
            
            color = "#0a7a3a" if status == "SUPPORTED" else ("#d97706" if status in ("TENTATIVE", "MIXED") else "#c0392b")
            
            flow.append(to_para(f"<b>Theme: {topic}</b> &nbsp;&nbsp; [<font color='{color}'><b>{status} / {band}</b></font>]", h3))
            flow.append(to_para(statement, body))
            
            why = c.get("why", {})
            supports = why.get("supports", [])
            contradictions = why.get("contradictions", [])
            citations = why.get("citations", [])
            
            if supports:
                flow.append(to_para("&nbsp;&nbsp;<b>Supported by:</b>", body_small))
                for s in supports:
                    clean_s = s.replace("fact:", "Fact: ").replace("method_finding:", "Finding: ").replace("method:", "Method: ")
                    flow.append(to_para(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; {clean_s}", body_small))
            
            if contradictions:
                flow.append(to_para("&nbsp;&nbsp;<b>Contradicted by:</b>", body_small))
                for ct in contradictions:
                    clean_ct = ct.replace("fact:", "Fact: ").replace("method_finding:", "Finding: ").replace("method:", "Method: ")
                    flow.append(to_para(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; {clean_ct}", body_small, textColor=RED))
            
            if citations:
                flow.append(to_para("&nbsp;&nbsp;<b>Traceable Citations:</b>", body_small))
                for cit in citations:
                    clean_cit = cit.replace("citation:", "")
                    flow.append(to_para(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; {clean_cit}", body_small, textColor=PURPLE))
            flow.append(Spacer(1, 0.3*cm))
    else:
        flow.append(to_para("No active claims generated for this chart.", body))
    flow.append(Spacer(1, 0.4*cm))
    
    # 3. Method Coverage
    flow.append(to_para("<b>Method Coverage & Availability:</b>", h2))
    cov = tr.get("method_coverage", {})
    if cov:
        cov_rows = [["METHOD FAMILY", "STATUS", "SAFE CODE"]]
        for method, info in sorted(cov.items()):
            state = info.get("state", "").upper()
            code = info.get("safe_code", "OK")
            color = "#0a7a3a" if state == "AVAILABLE" else "#c0392b"
            cov_rows.append([
                Paragraph(f"<b>{method.upper()}</b>", body_small),
                Paragraph(f"<font color='{color}'><b>{state}</b></font>", body_small),
                Paragraph(code, body_small)
            ])
        t_cov = Table(cov_rows, colWidths=[5.0*cm, 4.0*cm, 5.0*cm])
        t_cov.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), INDIGO),
            ("TEXTCOLOR", (0,0), (-1,0), CREAM),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ]))
        flow.append(t_cov)
        
    return flow
"""

if "def build_truth_report_section" not in code:
    code = code.replace("def generate(chart_path,out_name):", func_code + "\n\ndef generate(chart_path,out_name):")
    print("Function build_truth_report_section added.")
else:
    print("Function build_truth_report_section already present.")

# 2. Append truth_flow before doc.build(flow)
append_code = """
    # ─── TRUTH REPORT SECTION ───
    try:
        truth_flow = build_truth_report_section(chart)
        flow.extend(truth_flow)
    except Exception as exc:
        print(f"[truth_report] WARNING: {exc}")

    print(f"Building PDF for {chart['name']} with {len(flow)} elements...")
"""

if "truth_flow = build_truth_report_section(chart)" not in code:
    code = code.replace("print(f\"Building PDF for {chart['name']} with {len(flow)} elements...\")", append_code)
    print("Truth report append code added.")
else:
    print("Truth report append code already present.")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch complete.")
