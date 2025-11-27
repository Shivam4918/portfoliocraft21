import os
from dotenv import load_dotenv


load_dotenv(dotenv_path=r"D:\portfoliocraft\PortfolioCraft\.env")

key = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY found?", bool(key))
if key:
    print("First/last 4 chars:", key[:4] + "..." + key[-4:])
else:
    print("❌ Key not loaded from .env")
