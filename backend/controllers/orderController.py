from services.orderServices import createOrderServices

async def createOrderController(data):
    res_obj=await createOrderServices(data)
    return res_obj