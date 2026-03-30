# from fastapi import FastAPI
# from beanie import init_beanie

# from routes.authRoute import router as AuthRouter
# from routes.productRoute import router as ProductRouter
# from routes.orderRoute import router as orderRouter
# from routes.couponRoute import router as couponRouter
# #fastapi instance

# app=FastAPI()


# @app.get('/',tags=['health'])
# def healthRoute():
#     return {
#         'msg':'Server is working correctly'
#     }
    
# app.include_router(AuthRouter)
# app.include_router(ProductRouter)
# app.include_router(orderRouter)
# app.include_router(couponRouter)
from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models.orderModel import Order, Payment, Coupon
from config.Env import EnvConfig  # ✅ db.py se nahi, seedha URI use karo
from routes.authRoute import router as AuthRouter
from routes.productRoute import router as ProductRouter
from routes.orderRoute import router as orderRouter
from routes.couponRoute import router as couponRouter

app = FastAPI()

@app.on_event("startup")
async def startup():
    client = AsyncIOMotorClient(EnvConfig.MONGO_URI)  # ✅ naya client banao
    db = client[EnvConfig.DB_NAME]
    await init_beanie(
        database=db,
        document_models=[Order, Payment, Coupon]
    )

@app.get('/', tags=['health'])
def healthRoute():
    return {'msg': 'Server is working correctly'}

app.include_router(AuthRouter)
app.include_router(ProductRouter)
app.include_router(orderRouter)
app.include_router(couponRouter)