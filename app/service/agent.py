import mimetypes
from app.config.config import Settings
from app.utils.encoder import Encoder
from app.utils.pdf_extractor import Pdfextractor

class Agent:
    def __init__(self):
        self.model = Settings.get_model()
    
    def build_prompt(self) -> str:
        return (
            "Analisis file ini dan kembalikan hasil dalam format yang sangat ringkas:\n"
            "- Jika ada objek, sebutkan jumlah dan nama objek, pisahkan dengan koma jika lebih dari satu.\n"
            #"- Jika ada dokumen, sebutkan jenis dokumen (contoh: '1 surat kepemilikan tanah', '1 KTP').\n"
            "- Berikan balasan yang seragam, seperti '1 Cincin emas dengan pertama biru' menjadi '1 Cincin Emas'"
            #"- '1 Surat Kepemilikan Tanah di Kota Jakarta' menjadi '1 Surat Kepemilikan Tanah'"
            "- Hanya analisa objek yang berupa emas seperti perhiasan atau batangan emas"
            "- Jangan beri kalimat tambahan, jangan beri kata pengantar.\n"
            "- Hanya kembalikan daftar objek/dokumen yang ditemukan."
        )

    def analyze_file(self, file_path: str, mime_type:str = None) -> str:
        print(f"DEBUG: File {file_path} | MIME dari UI: {mime_type}")
        parts = []
        # mime_type, _ = mimetypes.guess_type(file_path)

        if not mime_type or mime_type == "application/octet-stream":
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            print(f"DEBUG: MIME fallback dari mimetypes: {mime_type}")

        # 🔧 Fallback manual kalau tetap None
        if not mime_type:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif ext == ".png":
                mime_type = "image/png"
            elif ext == ".pdf":
                mime_type = "application/pdf"

        if not mime_type:
            raise ValueError(f"❌ Tidak bisa mengenali tipe file: {file_path}")
        
        # PDF handling
        if mime_type == "application/pdf":
            text = Pdfextractor.exctract_doc(file_path)
            if text:
                parts.append({"text": text})
            else:
                base64_data = Encoder.file_to_base64(file_path)
                parts.append({"inline_data": {"mime_type": "application/pdf", "data": base64_data}})
        elif mime_type.startswith("image/"):
            base64_data = Encoder.file_to_base64(file_path)
            parts.append({"inline_data": {"mime_type": mime_type, "data": base64_data}})
        else:
            raise ValueError(f"Mime type '{mime_type}' tidak didukung")
        
        prompt = self.build_prompt()
        response = self.model.generate_content([{"text": prompt}, *parts])
        return response.text