import sys
import os

# --- הנדסת נתיבים כדי למצוא את ה"אחיינים" ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
services_path = os.path.join(project_root, "Services")
sys.path.append(services_path)

try:
    from transform import PDFToTextExtractor
    # וודאי ששם הקובץ ב-Services הוא parser.py או שחקי עם השם כאן
    from parser import AttendanceParser 
    print("הייבוא הצליח!")
except ImportError as e:
    print(f"שגיאה בייבוא: {e}")
    sys.exit(1)

def run_integration_test():
    pdf_path = os.path.join(project_root, "Repositories", "n_r_10_n.pdf")
    
    print(f"ניגש לקובץ בנתיב: {pdf_path}")
    
    extractor = PDFToTextExtractor()
    raw_text = extractor.process_pdf(pdf_path)
    
    if "שגיאה" in raw_text:
        print(raw_text)
        return

    parser = AttendanceParser()
    structured_data = parser.clean_text(raw_text)
    
    if not structured_data:
        print("הפרסר לא מצא נתונים.")
    else:
        print("\n=== טבלת נתונים סופית ומסודרת ===")
        # יצרתי כותרת יפה שמסבירה מה רואים בכל עמודה
        print(f"{'תאריך':<11} | {'יום':<8} | {'כניסה':<7} | {'יציאה':<7} | {'סהנ כ שעות'}")
        print("-" * 55)
        
        for row in structured_data:
            # כאן אנחנו ניגשים למפתחות החדשים שיצרנו ב-Parser
            print(f"{row['date']:<11} | {row['day']:<8} | {row['start']:<7} | {row['end']:<7} | {row['duration']} שעות")

if __name__ == "__main__":
    run_integration_test()