from config.Env import EnvConfig
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(EnvConfig.MONGO_URI)
db = client[EnvConfig.DB_NAME]



#collection 
user_collection=db['users']
product_collection=db['product']