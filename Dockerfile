# Gunakan image python slim
FROM python:3.11-slim

# Set workdir ke /app (folder ini akan berisi kode dari folder app/)
WORKDIR /code

# Copy requirements.txt ke container dan install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy semua kode (termasuk folder app/, config/, dll)
COPY . .

# Expose port 8000 untuk FastAPI
EXPOSE 8000

# Jalankan uvicorn dengan path sesuai struktur project
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
