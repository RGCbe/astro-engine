import os
import subprocess

pdf_files = ['/opt/astro/knowledge/dorotheus1.pdf', '/opt/astro/knowledge/dorotheus2.pdf', '/opt/astro/knowledge/dorotheus3.pdf']
txt_files = ['/opt/astro/knowledge/dorotheus1.txt', '/opt/astro/knowledge/dorotheus2.txt', '/opt/astro/knowledge/dorotheus3.txt']

for pdf in pdf_files:
    subprocess.run(['pdftotext', pdf])

combined_text = ""
for txt in txt_files:
    with open(txt, 'r', encoding='utf-8', errors='ignore') as f:
        combined_text += f.read() + "\n"

with open('/opt/astro/knowledge/CarmenAstrologicum_raw.txt', 'w', encoding='utf-8') as f:
    f.write(combined_text)
