FROM python:3.10-slim

# Cài đặt FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Tạo thư mục app
WORKDIR /app

# Copy và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Tạo thư mục chứa file để tránh lỗi quyền ghi
RUN mkdir -p uploads outputs && chmod 777 uploads outputs

# Chạy app (Hugging Face mặc định chạy port 7860)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]