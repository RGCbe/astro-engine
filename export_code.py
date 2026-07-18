import os
import sys
from fpdf import FPDF

class CodePDF(FPDF):
    def header(self):
        self.set_font('Courier', 'B', 10)
        self.cell(0, 10, 'Astro Project - Source Code Export', 0, 0, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Courier', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def get_all_code_files(base_dir):
    code_files = []
    exclude_dirs = {'.git', '__pycache__', 'venv', 'reports', 'node_modules', '.gemini'}
    valid_exts = {'.py', '.html', '.css', '.js', '.md', '.json'}
    
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_exts:
                code_files.append(os.path.join(root, f))
    return sorted(code_files)

def export_code_to_pdfs(base_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    files = get_all_code_files(base_dir)
    
    pdf_index = 1
    current_pdf = CodePDF()
    current_pdf.add_page()
    current_pdf.set_auto_page_break(auto=True, margin=15)
    current_pdf.set_font('Courier', '', 8)
    
    # Approx limit: 300kb usually correlates to around 50-80 pages of dense text. 
    # We will split arbitrarily at 60 pages to stay around the 300KB mark.
    MAX_PAGES_PER_PDF = 60 

    for filepath in files:
        rel_path = os.path.relpath(filepath, base_dir)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            continue # Skip binary or weirdly encoded files
            
        # Add file header
        current_pdf.set_font('Courier', 'B', 10)
        current_pdf.set_text_color(200, 50, 50)
        current_pdf.multi_cell(0, 8, f"\n\n{'='*60}\nFILE: {rel_path}\n{'='*60}\n")
        
        current_pdf.set_font('Courier', '', 8)
        current_pdf.set_text_color(0, 0, 0)
        
        # Add content lines safely
        for raw_line in content.split('\n'):
            safe_line = raw_line.encode('latin-1', 'replace').decode('latin-1').replace('?', ' ')
            # Chunk long lines to prevent overflow
            chunks = [safe_line[i:i+80] for i in range(0, max(1, len(safe_line)), 80)]
            if not chunks:
                current_pdf.ln(4)
            for chunk in chunks:
                current_pdf.set_x(15)
                current_pdf.cell(0, 4, chunk)
                current_pdf.ln(4)
            
            if current_pdf.page_no() >= MAX_PAGES_PER_PDF:
                out_path = os.path.join(output_dir, f'engine_code_part_{pdf_index}.pdf')
                current_pdf.output(out_path)
                print(f"Saved {out_path} (Size: {os.path.getsize(out_path)//1024} KB)")
                
                pdf_index += 1
                current_pdf = CodePDF()
                current_pdf.add_page()
                current_pdf.set_auto_page_break(auto=True, margin=15)
                current_pdf.set_font('Courier', '', 8)

    # Save any remaining content
    if current_pdf.page_no() > 1 or current_pdf.get_y() > 20:
        out_path = os.path.join(output_dir, f'engine_code_part_{pdf_index}.pdf')
        current_pdf.output(out_path)
        print(f"Saved {out_path} (Size: {os.path.getsize(out_path)//1024} KB)")

if __name__ == '__main__':
    project_dir = r"f:\astro"
    output_directory = r"f:\astro\engine_code_export"
    export_code_to_pdfs(project_dir, output_directory)
    print("Export complete.")
