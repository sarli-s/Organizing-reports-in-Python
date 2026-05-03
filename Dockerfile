FROM python:3.11-slim-bookworm

# הגדרת משתני סביבה לעברית
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# הגדרת נתיב הנתונים הסטנדרטי בלינוקס
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata/


# התקנת תלויות מערכת
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    tesseract-ocr \
    tesseract-ocr-heb \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    # הוספת פונטים קריטית לעברית
    fonts-noto-core \
    fonts-freefont-ttf \
    fontconfig \
    # תלויות לעיבוד תמונה וקובצי PDF
    libmagic1 \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# # וידוא שהנתיב קיים ויש בו את קבצי השפה
# RUN mkdir -p /usr/share/tesseract-ocr/tessdata

# יצירת תיקיית קישור לביטחון (אם הספרייה מחפשת תחת תיקיית "5")
RUN mkdir -p /usr/share/tesseract-ocr/5/ && \
    ln -s /usr/share/tesseract-ocr/tessdata /usr/share/tesseract-ocr/5/tessdata || true

# # פקודה זו מוודא שגם אם המערכת התקינה את זה במיקום אחר, הקישור יהיה תקין
# RUN ln -s /usr/share/tesseract-ocr/tessdata /usr/share/tesseract-ocr/5/tessdata || true


# רענון מאגר הפונטים במערכת
RUN fc-cache -f -v

WORKDIR /app

# יצירת תיקיית פלט
RUN mkdir -p /app/output && chmod 777 /app/output

COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY . .

# וודאי שהפקודה הזו מתאימה לשם הקובץ הראשי שלך
ENTRYPOINT ["python", "main.py"]