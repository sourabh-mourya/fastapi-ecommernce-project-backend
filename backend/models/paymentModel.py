from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId
from models.orderModel import PaymentMethod, PaymentGatewayStatus
from datetime import datetime, timezone
from typing import Optional

class PaymentInitiate(BaseModel):
    order_id: str
    payment_method: PaymentMethod

class PaymentVerify(BaseModel):
    order_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class Payment(Document):
    order_id: PydanticObjectId
    user_id: PydanticObjectId
    gateway: PaymentMethod
    razorpay_order_id: Optional[str] = None
    transaction_id: Optional[str] = None
    gateway_signature: Optional[str] = None
    amount: float
    currency: str = "INR"
    status: PaymentGatewayStatus = PaymentGatewayStatus.INITIATED
    initiated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    paid_at: Optional[datetime] = None

    class Settings:
        name = "payments"
        
        
class PaymentRefund(BaseModel):
    order_id: str