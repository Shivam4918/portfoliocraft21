# config.py
import os
from dotenv import load_dotenv

load_dotenv()  

class Config:
   
    SECRET_KEY = os.getenv("43f3ac0a3098fe2d938e83513236918ad9beb0a9c4063eba46da698f74d72c3d", "dev_secret_key")  
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///instance/portfolio.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", "uploads")
    PROFILE_PICS_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", "profile_pics")
    ALLOWED_EXTENSIONS = {"pdf"}

   
    GEMINI_API_KEY = os.getenv("AIzaSyD9LKzuUEAFnVZgT9mcmMM9Qr-JDyOFS0Y")

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROFILE_PICS_FOLDER, exist_ok=True)
