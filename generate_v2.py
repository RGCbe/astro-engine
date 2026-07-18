import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from engine.chart import compute_chart
from engine.client_report_v2 import generate_client_report_v2

def main():
    chart = compute_chart(
        name="Manoj Kumar",
        date="1996-05-25",
        time="20:25",
        tz_hours=5.5,
        place="Coimbatore",
        lat=11.25,
        lon=77.12
    )
    
    report_md = generate_client_report_v2(chart)
    
    with open('C:\\Users\\chive\\.gemini\\antigravity\\brain\\25a79dbb-7d96-41f7-97d3-17026254857e\\Manoj_Kumar_Full_V2_Report.md', 'w', encoding='utf-8') as f:
        f.write(report_md)
        
if __name__ == '__main__':
    main()
