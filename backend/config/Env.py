from dotenv import load_dotenv
import os

load_dotenv()


class EnvConfig:
    DB_NAME = os.getenv("DB_NAME")
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_AUTH=os.getenv('JWT_AUTH')
    RAZORPAY_KEY_ID=os.getenv('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET=os.getenv('RAZORPAY_KEY_SECRET')
    RAZORPAY_WEBHOOK_SECRET=os.getenv('RAZORPAY_WEBHOOK_SECRET')
    
    