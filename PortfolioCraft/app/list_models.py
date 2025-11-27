import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(dotenv_path=r"D:\portfoliocraft\PortfolioCraft\.env")
api = os.getenv("GEMINI_API_KEY")
print("Key present?", bool(api))
genai.configure(api_key=api)
try:
    models = genai.list_models()
    print("RAW models output:")
    print(models)
    
    try:
        for m in models:
            print(" -", getattr(m, "name", m))
    except Exception:
        pass
except Exception as e:
    print("list_models() error:", e)
