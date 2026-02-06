import base64
from PIL import Image
import io

class Encoder:
    @staticmethod
    def file_to_base64(file_path: str, max_size=1024) -> str:
        with open(file_path, "rb") as f:
            mime_type = "image/jpeg" if file_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
            
            # Jika file adalah gambar, resize dulu
            try:
                img = Image.open(f)
                
                # Convert to RGB if RGBA (to save as JPEG)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Resize logic
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    # print(f"DEBUG: Resized image to {new_size}")

                # Save to buffer
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                file_bytes = buffer.getvalue()
            except Exception as e:
                # Fallback jika bukan gambar valid atau error lain, baca raw bytes
                print(f"WARN: Gagal resize image, menggunakan raw. Error: {e}")
                f.seek(0)
                file_bytes = f.read()

            return base64.b64encode(file_bytes).decode("utf-8")