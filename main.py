import os
import sys
import re
import random
from datetime import datetime, timedelta

# הוספת נתיב הסרביסים
current_dir = os.path.dirname(os.path.abspath(__file__))
services_path = os.path.join(current_dir, "Services")
if services_path not in sys.path:
    sys.path.append(services_path)

from transform import PDFToTextExtractor
from clasification import DocumentClassifier
from parser import ParserA, ParserN

def shift_time_randomly(time_str, max_minutes=20):
    """מזיז את השעה ברנדומליות של עד 20 דקות"""
    try:
        fmt = "%H:%M"
        dt = datetime.strptime(time_str, fmt)
        random_shift = random.randint(-max_minutes, max_minutes)
        new_time = dt + timedelta(minutes=random_shift)
        return new_time.strftime(fmt)
    except:
        return time_str

def run_pipeline(file_name):
    # 1. חילוץ טקסט
    pdf_path = os.path.join(current_dir, "Repositories", file_name)
    if not os.path.exists(pdf_path):
        print(f"שגיאה: הקובץ {file_name} לא נמצא בתיקיית Repositories")
        return

    print(f"--- מתחיל תהליך עבור: {file_name} ---")
    extractor = PDFToTextExtractor()
    raw_text = extractor.process_pdf(pdf_path)
    
    if "שגיאה" in raw_text:
        print(raw_text)
        return

    # 2. סיווג
    classifier = DocumentClassifier()
    doc_type = classifier.classify(raw_text)
    print(f"הקובץ זוהה כסוג: {doc_type}")

    # 3. בחירת פרסר
    parser = ParserA() if doc_type == "A" else ParserN()

    # 4. ניקוי ועיבוד נתונים
    structured_data = []
    lines = raw_text.split('\n')
    
# ... בתוך run_pipeline ...
    for line in lines:
        # ניקוי השורה לפני הכל - זה מה שפותר את סוג A
        clean_line = line.replace('"', '').replace("'", "")
        
        # מחפשים תאריך בשורה המנוקה
        date_match = re.search(parser.date_pattern, clean_line)
        if not date_match:
            continue
            
        date_str = date_match.group(1)
        
        # מחלצים נתונים מהשורה המנוקה
        row_data = parser.parse_line(clean_line)
        
        if row_data:
            row_data["date"] = date_str
            structured_data.append(row_data)

    # 5. הצגת תוצאות עם טרנספורמציה (20 דקות)
    print(f"\n=== טבלת נתונים סופית (סוג {doc_type}) ===")
    
    if doc_type == "A":
        header = f"{'תאריך':<12} | {'כניסה חדשה':<10} | {'יציאה חדשה':<10} | {'הפסקה':<7} | {'סה\"כ שעות'}"
    else:
        header = f"{'תאריך':<12} | {'כניסה חדשה':<10} | {'יציאה חדשה':<10} | {'סה\"כ שעות'}"
    
    print(header)
    print("-" * len(header))

    for row in structured_data:
        # טרנספורמציה רנדומלית
        new_start = shift_time_randomly(row['start'])
        new_end = shift_time_randomly(row['end'])
        
        # וולידציה: שעת כניסה לא אחרי יציאה
        if datetime.strptime(new_start, "%H:%M") >= datetime.strptime(new_end, "%H:%M"):
            # תיקון אוטומטי במקרה של התנגשות (מוסיף שעתיים כברירת מחדל)
            temp_dt = datetime.strptime(new_start, "%H:%M") + timedelta(hours=2)
            new_end = temp_dt.strftime("%H:%M")

        # הדפסה לפי סוג
        if doc_type == "A":
            print(f"{row['date']:<12} | {new_start:<10} | {new_end:<10} | {row['break']:<7} | {row['duration']} שעות")
        else:
            print(f"{row['date']:<12} | {new_start:<10} | {new_end:<10} | {row['duration']} שעות")

if __name__ == "__main__":  
    # הריצי על קובץ אחד בכל פעם לבדיקה
    target_file = "a_r_9.pdf" #"n_r_5_n.pdf" # או 
    run_pipeline(target_file)