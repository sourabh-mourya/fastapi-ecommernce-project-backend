from fastapi import APIRouter, Depends
from models.paymentModel import PaymentInitiate,PaymentVerify,PaymentRefund
from middleware.verfiyToken import verifyToken
from routes.authRoute import requireRole
from controllers.paymentController import initiatePaymentController,verifyPaymentController,refundPaymentController

router = APIRouter(prefix="/api/v1/payment", tags=["payment"])


@router.post("/initiate")
async def paymentInitiate(data: PaymentInitiate, user=Depends(verifyToken)):
    return await initiatePaymentController(data, user["_id"])


@router.post('/verify')
async def verifyPayment(data:PaymentVerify,user=Depends(verifyToken)):
        return await verifyPaymentController(data)
    
    
@router.post('/refund')
async def refundPayment(data: PaymentRefund, user=Depends(requireRole('admin'))):
    return await refundPaymentController(data, user)
