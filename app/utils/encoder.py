import base64

class Encoder:
    def file_to_base64(file_path:str) -> str:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            return base64.b64encode(file_bytes).decode("utf-8")