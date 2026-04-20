import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image

# נתיבים (תוודאי שהם נכונים אצלך)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\Program Files\poppler\poppler-24.02.0\Library\bin'

class PDFToTextExtractor:
    def process_pdf(self, pdf_path):
        try:
            # 1. המרה לתמונה באיכות גבוהה מאוד
            print("ממיר PDF לתמונה...")
            images = convert_from_path(pdf_path, dpi=400, poppler_path=POPPLER_PATH)
            
            full_text = ""
            for i, img in enumerate(images):
                # --- שלב שיפור התמונה (הסוד להצלחה) ---
                # הופכים את התמונה למערך של מספרים (OpenCV)
                open_cv_image = np.array(img)
                # הפיכה לשחור לבן (Grayscale)
                gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)
                # הגדלת הניגודיות - גורם לטקסט להיות שחור חזק והרקע לבן נקי
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # שמירה זמנית של התמונה המעובדת כדי לראות אם היא ברורה (אופציונלי)
                processed_img = Image.fromarray(thresh)
                
                print(f"מפענח עמוד {i+1} אחרי שיפור תמונה...")
                # הרצת ה-OCR על התמונה הנקייה
                text = pytesseract.image_to_string(processed_img, lang='heb+eng', config='--psm 6')
                full_text += text
                
            return full_text
        except Exception as e:
            return f"שגיאה: {str(e)}"

if __name__ == "__main__":
    extractor = PDFToTextExtractor()
    result = extractor.process_pdf("../Repositories/n_r_5_n.pdf")
    print("\n--- תוצאה חדשה (אמורה להיות הרבה יותר מפורטת): ---")
    print(result)