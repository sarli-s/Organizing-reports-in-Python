# FROM python:3.11-slim

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     tesseract-ocr \
#     tesseract-ocr-heb \
#     poppler-utils \
#     libglib2.0-0 \
#     libsm6 \
#     libxrender1 \
#     libxext6 \
#     libgl1 \
#     xfonts-75dpi \
#     xfonts-base \
#     fontconfig \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Install wkhtmltopdf from local file
# COPY wkhtmltox_0.12.6.1-3.bookworm_amd64.deb /tmp/
# RUN apt-get update && apt-get install -y /tmp/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
#     && rm /tmp/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# COPY . .

# RUN mkdir -p /output

# ENTRYPOINT ["python", "main.py"]
# CMD ["--help"]

# בסיס - Python עם כלים למערכת
FROM python:3.11-slim

# התקנת תלויות מערכת (נדרש עבור tesseract, opencv, pdf2image)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-heb \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# תיקיית עבודה בתוך הקונטיינר
WORKDIR /app

# העתק requirements והתקן תחילה (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# העתק את שאר קבצי הפרויקט
COPY . .

# הפקודה להרצה
CMD ["python", "main.py"]