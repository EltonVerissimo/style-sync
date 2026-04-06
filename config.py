import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')

    def __init__(self):
        if not self.MONGO_URI:
            raise Exception("MONGO_URI não configurada!")
        
        if not self.SECRET_KEY:
            raise Exception("SECRET_KEY não configurada!")