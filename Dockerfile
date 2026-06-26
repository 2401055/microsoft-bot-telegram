# استخدم صورة بايثون الرسمية
FROM python:3.11-slim

# تثبيت المتطلبات الأساسية للمتصفح
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# إعداد مجلد العمل
WORKDIR /app

# نسخ الملفات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت Playwright Chromium فقط
RUN playwright install chromium --with-deps

# نسخ باقي الكود
COPY . .

# تشغيل البوت
CMD ["python", "microsoft_bot.py"]
