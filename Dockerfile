# Sử dụng image Python 3.9
FROM python:3.11-slim

WORKDIR /app

# Copy và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Chạy ứng dụng
CMD ["python", "app.py"]