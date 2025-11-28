# api.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil, os, mimetypes

from app.service.agent import Agent
from app.config.auth import Authuser

app = FastAPI(title="Document Analysis API", version="1.0.0")
agent = Agent()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/analyze-file/")
async def analyze_file(username : Authuser, file: UploadFile = File(...)):
    try:
        # Validasi tipe file
        if not file.content_type.startswith(("image/", "application/pdf")):
            raise HTTPException(status_code=400, detail="Hanya mendukung file gambar atau PDF")

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Simpan file ke disk sementara
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Panggil agent untuk analisis
        result = agent.analyze_file(file_path, mime_type=file.content_type)

        # Hapus file setelah selesai (optional, bisa simpan kalau mau logging)
        os.remove(file_path)

        return JSONResponse(content={"result": result})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
