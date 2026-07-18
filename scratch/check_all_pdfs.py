import os
import re
import sys
import pypdf
from pathlib import Path

# Add project root to path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

PDF_FILES = [
    # Shifting report
    "reports/2026/07/14/pdf/House_Shifting_Muhurtha_Report.pdf",
    # S. Padmapriyanka (செம்பன்)
    "reports/2026/07/14/pdf/Manoj_S_Padmapriyanka_Compatibility_Report_TA.pdf",
    "reports/2026/07/14/pdf/Manoj_S_Padmapriyanka_Compatibility_Report_EN.pdf",
    # P. Sashtika (மணியன்)
    "reports/2026/07/14/pdf/Manoj_P_Sashtika_Compatibility_Report_TA.pdf",
    "reports/2026/07/14/pdf/Manoj_P_Sashtika_Compatibility_Report_EN.pdf",
    # N. Gomathi (ஆந்தை)
    "reports/2026/07/14/pdf/Manoj_N_Gomathi_Compatibility_Report_TA.pdf",
    "reports/2026/07/14/pdf/Manoj_N_Gomathi_Compatibility_Report_EN.pdf",
]

def run_qa_audit(file_path):
    full_path = _ROOT / file_path
    if not full_path.exists():
        return {"exists": False, "error": "File does not exist"}
        
    try:
        reader = pypdf.PdfReader(str(full_path))
        num_pages = len(reader.pages)
        
        # 1. Extract text and analyze characters
        full_text = ""
        page_lengths = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            full_text += txt
            page_lengths.append(len(txt.strip()))
            
        # 2. Check for replacement glyphs or invalid symbols
        tofu_found = "\ufffd" in full_text
        
        # 3. Check for specific language leakages
        is_tamil_report = "_TA.pdf" in file_path or "Tamil" in file_path
        
        # Find Latin characters in Tamil reports
        latin_characters = []
        if is_tamil_report:
            # Match any word containing English letters
            latin_characters = re.findall(r'[A-Za-z]+', full_text)
            # Filter out known allowed font names or metadata if extracted, but otherwise want it empty
            # NotoSansTamil might extract layout text, so let's check for any actual English words
            latin_characters = [w for w in latin_characters if w not in ["Page", "ASTROMYSTIC", "MUHURTHA", "CONSULTATION"]]
            
        # Find Tamil characters in English reports
        tamil_characters = []
        if not is_tamil_report and "House_Shifting" not in file_path:
            # Tamil unicode block is 0B80 to 0BFF
            tamil_characters = [c for c in full_text if 0x0B80 <= ord(c) <= 0x0BFF]
            
        # 4. Font checking
        fonts_used = set()
        helvetica_substituted = False
        for page in reader.pages:
            if "/Resources" in page and "/Font" in page["/Resources"]:
                fonts = page["/Resources"]["/Font"]
                helvetica_keys = []
                for f_key, f_obj in fonts.items():
                    if "/BaseFont" in f_obj:
                        bf = f_obj["/BaseFont"]
                        fonts_used.add(bf)
                        if "Helvetica" in bf or "Times" in bf:
                            helvetica_keys.append(f_key)
                
                # Check if the fallback font key is actually used in drawing
                if helvetica_keys:
                    content = page.get_contents()
                    content_str = ""
                    if isinstance(content, list):
                        content_str = b"".join(c.get_data() for c in content).decode("latin1")
                    elif content:
                        content_str = content.get_data().decode("latin1")
                    
                    for hk in helvetica_keys:
                        # Scan for font selection operator
                        if re.search(r'/' + re.escape(hk[1:]) + r'\b', content_str):
                            helvetica_substituted = True
                            break
                            
        # 5. Check for empty pages
        has_empty_page = any(length < 20 for length in page_lengths)
        
        return {
            "exists": True,
            "pages": num_pages,
            "fonts": list(fonts_used),
            "helvetica_substituted": helvetica_substituted,
            "tofu_found": tofu_found,
            "latin_leakage": list(set(latin_characters)),
            "tamil_leakage": len(tamil_characters) > 0,
            "page_lengths": page_lengths,
            "has_empty_page": has_empty_page,
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}

if __name__ == "__main__":
    print("==================================================")
    print("AstroMystic PDF Automated Quality Assurance Audit")
    print("==================================================\n")
    
    all_passed = True
    for f in PDF_FILES:
        print(f"Auditing: {f}")
        res = run_qa_audit(f)
        if not res["exists"]:
            print(f"  [ERROR] FAILED: {res['error']}")
            all_passed = False
            continue
            
        if "error" in res:
            print(f"  [ERROR] FAILED: {res['error']}")
            all_passed = False
            continue
            
        # Audit criteria evaluation
        failed_checks = []
        if res["helvetica_substituted"]:
            failed_checks.append("Font Substitution detected (Helvetica/Times fallback found)")
        if res["tofu_found"]:
            failed_checks.append("Tofu/Replacement characters (\\ufffd) found")
        if res["latin_leakage"]:
            failed_checks.append(f"English leakage in Tamil report: {res['latin_leakage']}")
        if res["tamil_leakage"]:
            failed_checks.append("Tamil leakage in English report")
        if res["has_empty_page"]:
            failed_checks.append(f"Empty page detected (page lengths: {res['page_lengths']})")
            
        if failed_checks:
            print("  [FAIL] FAILED CHECKS:")
            for c in failed_checks:
                print(f"    - {c}")
            all_passed = False
        else:
            print("  [PASS] PASSED ALL CHECKS")
            
        print(f"     Pages: {res['pages']} | Fonts Used: {res['fonts']}")
        print(f"     Page Lengths (chars): {res['page_lengths']}")
        print("-" * 50)
        
    if all_passed:
        print("\nSUCCESS: All generated PDF booklets passed 100% of the automated QA criteria!")
    else:
        print("\nWARNING: Some PDF booklets failed specific QA audit criteria. Please review.")
