from services.paymentServices import initiatePaymentServices,verifyPaymentServices,refundPaymentServices

async def initiatePaymentController(data,userId):
    res_obj=await initiatePaymentServices(data,userId)
    return res_obj


async def verifyPaymentController(data):
    res_obj=await verifyPaymentServices(data)
    return res_obj

async def refundPaymentController(data):
    res_obj=await refundPaymentServices(data)
    return res_obj