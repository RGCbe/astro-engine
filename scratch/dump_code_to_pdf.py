import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, XPreformatted, PageBreak
from reportlab.lib.colors import HexColor

def generate_source_pdf():
    out_file = r"f:\astro\AstroReport_OS_Full_Source_Code.pdf"
    doc = SimpleDocTemplate(out_file, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        textColor=HexColor('#0D1B2A'),
        spaceAfter=30
    )
    
    header_style = ParagraphStyle(
        'FileHeader', 
        parent=styles['Heading2'], 
        textColor=HexColor('#C9A84C'),
        backColor=HexColor('#0D1B2A'),
        spaceAfter=10,
        spaceBefore=15,
        leftIndent=5,
        rightIndent=5,
        borderPadding=5
    )
    
    code_style = ParagraphStyle(
        'Code',
        fontName='Courier',
        fontSize=7,
        leading=9,
        textColor=HexColor('#1A1A2E'),
        wordWrap='CJK'
    )

    story.append(Paragraph("AstroReport OS — Complete Source Code Reference", title_style))
    story.append(Paragraph("This document contains the complete source code, markdown documentation, and configuration files for the AstroReport OS engine, compiled for review and improvement.", styles['Normal']))
    story.append(PageBreak())

    base_dir = r"f:\astro"
    # Exclude non-source or huge directories
    exclude_dirs = {'.git', 'venv', '__pycache__', 'Books', '.gemini', 'scratch', 'marketing', 'reports', '.tempmediaStorage', 'node_modules', '.pytest_cache'}
    allowed_exts = {'.py', '.md', '.json', '.txt', '.yaml', '.yml', '.env.example'}
    
    # Specific huge files to skip
    exclude_files = {'MASTER_STRUCTURE_BASE.txt', 'package-lock.json'}

    file_count = 0

    for root, dirs, files in os.walk(base_dir):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in sorted(files):
            if file in exclude_files:
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext in allowed_exts:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, base_dir)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Skip empty files
                    if not content.strip():
                        continue
                        
                    # Cap extremely large files to prevent PDF crash
                    lines = content.split('\n')
                    if len(lines) > 2500:
                        content = '\n'.join(lines[:2500]) + '\n\n... [TRUNCATED DUE TO LENGTH] ...'

                    # Clean content for reportlab XML escaping
                    content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    
                    story.append(Paragraph(f"📄 {rel_path}", header_style))
                    story.append(XPreformatted(content, code_style))
                    story.append(Spacer(1, 15))
                    file_count += 1
                    
                except Exception as e:
                    print(f"Skipping {rel_path}: {e}")

    print(f"Processed {file_count} files. Building PDF...")
    doc.build(story)
    size_kb = os.path.getsize(out_file) // 1024
    print(f"[DONE] Generated {out_file} ({size_kb} KB)")

if __name__ == "__main__":
    generate_source_pdf()
