import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from engine.chart import compute_chart
from engine.chapters import build_chapters

def main():
    print("Computing chart...")
    chart = compute_chart(
        name="Manoj Kumar",
        date="1996-05-25",
        time="20:25",
        tz_hours=5.5,
        place="Coimbatore",
        lat=11.25,
        lon=77.12
    )
    
    print("Running build_chapters...")
    import engine.chapters
    import sys
    
    def traced_enrich(ch, chart):
        print(f"  Enriching {ch.planet}...")
        try:
            print("    detect_accident_patterns")
            from engine.accident import detect_accident_patterns
            detect_accident_patterns(chart)
        except Exception as e: print(e)
        
        try:
            print("    afflictions.detect_all")
            from engine.afflictions import detect_all
            detect_all(chart)
        except Exception as e: print(e)
        
        try:
            print("    blessings.detect_all")
            from engine.blessings import detect_all
            detect_all(chart)
        except Exception as e: print(e)
        
        try:
            print("    education.predict_subjects")
            from engine.education import predict_subjects
            predict_subjects(chart)
        except Exception as e: print(e)
        
        try:
            print("    life_domains.predict_marriage")
            from engine.life_domains import predict_marriage
            predict_marriage(chart)
        except Exception as e: print(e)
        
        try:
            print("    life_domains.predict_career")
            from engine.life_domains import predict_career
            predict_career(chart)
        except Exception as e: print(e)
        
        try:
            print("    life_domains.predict_foreign")
            from engine.life_domains import predict_foreign
            predict_foreign(chart)
        except Exception as e: print(e)
        print("  Done enriching.")

    engine.chapters._enrich_chapter_with_events = traced_enrich
    
    build_chapters(chart)
    print("Done!")
        
if __name__ == '__main__':
    main()
