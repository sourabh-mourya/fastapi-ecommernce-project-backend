from dotenv import load_dotenv
import os

load_dotenv()


class EnvConfig:
    DB_NAME = os.getenv("DB_NAME")
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_AUTH=os.getenv('JWT_AUTH')