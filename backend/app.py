from fastapi import FastAPI
from routes.authRoute import router as AuthRouter
from routes.productRoute import router as ProductRouter
from routes.orderRoute import router as orderRouter
from routes.couponRoute import router as couponRouter
#fastapi instance

app=FastAPI()


@app.get('/',tags=['health'])
def healthRoute():
    return {
        'msg':'Server is working correctly'
    }
    
app.include_router(AuthRouter)
app.include_router(ProductRouter)
app.include_router(orderRouter)
app.include_router(couponRouter)