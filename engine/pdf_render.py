"""
Reliable PDF renderer using fpdf2.
Optimized for Windows with no external GTK dependencies.
"""
from fpdf import FPDF

class VedicPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(176, 141, 87) # Gold
        self.cell(0, 10, '* Vedic Chart Reading - Classical Consensus *', 0, 0, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(176, 141, 87)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def render_pdf(markdown_text: str, output_path: str) -> str:
    """Convert consensus report markdown to a clean PDF using fpdf2."""
    pdf = VedicPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Basic Markdown-ish Parser for fpdf2
    lines = markdown_text.split('\n')
    for line in lines:
        pdf.set_x(10) # Reset to left margin
        # Sanitize for latin-1 core fonts
        line = line.encode('latin-1', 'replace').decode('latin-1').replace('?', ' ')
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
            
        if line.startswith('## '):
            pdf.set_font('helvetica', 'B', 16)
            pdf.set_text_color(42, 30, 92) # Deep Indigo
            pdf.ln(5)
            pdf.multi_cell(0, 10, line[3:])
            pdf.ln(2)
        elif line.startswith('### '):
            pdf.set_font('helvetica', 'B', 14)
            pdf.set_text_color(212, 131, 31) # Saffron
            pdf.ln(3)
            pdf.multi_cell(0, 8, line[4:])
        elif line.startswith('#### '):
            pdf.set_font('helvetica', 'B', 12)
            pdf.set_text_color(122, 31, 61) # Maroon
            pdf.multi_cell(0, 7, line[5:])
        elif line.startswith('> '):
            pdf.set_font('helvetica', 'I', 10)
            pdf.set_text_color(85, 85, 85) # Slate
            pdf.set_x(20) 
            pdf.multi_cell(170, 6, line[2:])
        elif '<div' in line or '</div>' in line:
            # Skip HTML gauge blocks for now in fpdf2
            continue
        else:
            pdf.set_font('helvetica', '', 11)
            pdf.set_text_color(58, 58, 74) # Dark Slate
            pdf.multi_cell(0, 6, line.replace('**', '').replace('*', ''))
            
    pdf.output(output_path)
    return output_path
