from fastapi import APIRouter,Depends
from models.orderModel import Order
from controllers.orderController import createOrderController
router=APIRouter(prefix='/api/v1/order',tags=['order'])


@router.post('/create_order')
async def createOrder(data:Order):
    return await createOrderController(data)


