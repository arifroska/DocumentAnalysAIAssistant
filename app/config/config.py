import os
from dotenv import load_dotenv
import google.generativeai as genai

class Settings:
    load_dotenv()
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = "gemini-2.5-pro"

    TEMPERATURE: float = 0.0
    TOP_P: float = 0.5
    TOP_K: float = 0.5

    @staticmethod
    def get_model():
        if not Settings.GEMINI_API_KEY:
            raise ValueError("API Key tidak ditemukan")
        genai.configure(api_key=Settings.GEMINI_API_KEY)
        return genai.GenerativeModel(
            model_name=Settings.MODEL_NAME
            generation_config={
                "temperature": Settings.TEMPERATURE,
                "top_p": Settings.TOP_P,
                "top_k": Settings.TOP_K
            }
        )