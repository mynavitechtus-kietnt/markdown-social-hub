# Dockerfile

# Bước 1: Chọn image nền
FROM python:3.12-slim

# Bước 2: Thiết lập thư mục làm việc
WORKDIR /app

# Bước 3: Cài đặt dependencies hệ thống (cho PostgreSQL + Pillow)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Bước 4: Copy và cài đặt Python dependencies (tách riêng để Docker cache tối ưu)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bước 5: Copy source code
COPY . .

# Bước 6: Tạo thư mục logs và media
RUN mkdir -p logs media

# Bước 7: Expose port
EXPOSE 8000

# Bước 8: Chạy ứng dụng (dùng runserver cho dev, gunicorn cho prod)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
