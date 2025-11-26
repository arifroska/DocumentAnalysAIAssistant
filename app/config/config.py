import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class Settings:
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    #MODEL_NAME = "gemini-2.5-pro"
    MODEL_NAME = "gemini-3-pro-preview"

    TEMPERATURE: float = 0.0
    TOP_P: float = 0.5
    TOP_K: int = 5

    @staticmethod
    def get_model():
        if not Settings.GEMINI_API_KEY:
            raise ValueError("API Key tidak ditemukan")
        genai.configure(api_key=Settings.GEMINI_API_KEY)
        return genai.GenerativeModel(
            model_name=Settings.MODEL_NAME,
            generation_config={
                "temperature": Settings.TEMPERATURE,
                "top_p": Settings.TOP_P,
                "top_k": Settings.TOP_K
            }
        )
    
class Dbconfig:

    DB_USER = os.getenv('DBUSER')
    DB_PASS = os.getenv('DBPASS')
    DB_HOST = os.getenv('DBHOST')
    DB_PORT = os.getenv('DBPORT')
    DB_NAME = os.getenv('DBNAME')

    DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    TABLE_NAME = os.getenv('TABLENAME')