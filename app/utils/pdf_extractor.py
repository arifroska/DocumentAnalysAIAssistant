import fitz

class Pdfextractor:
    @staticmethod
    def exctract_doc(file_path:str) -> str:
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            doc.close()
            return text.strip()
        except Exception as e:
            print(f"Gagal membaca PDF : {e}")
            return ""
