from datetime import datetime, timezone
from typing import Annotated, Optional
from enum import Enum
from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    RAZORPAY = "razorpay"
    STRIPE = "stripe"
    COD = "cod"


class PaymentGatewayStatus(str, Enum):
    INITIATED = "initiated"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class CouponType(str, Enum):
    PERCENTAGE = "percentage"
    FLAT = "flat"


# ---------------------------------------------------------------------------
# Embedded sub-documents (not separate collections)
# ---------------------------------------------------------------------------


class AddressSnapshot(BaseModel):
    full_name: str
    phone: str
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str = "India"


class OrderItem(BaseModel):
    product_id: PydanticObjectId
    product_name: str
    product_image: Optional[str] = None
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class CouponSnapshot(BaseModel):
    coupon_id: PydanticObjectId
    code: str
    type: CouponType
    value: float
    discount_amount: float


# ---------------------------------------------------------------------------
# ORDER
# ---------------------------------------------------------------------------


from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from beanie import Document, PydanticObjectId


class Order(Document):
    order_number: str = Field(..., unique=True)
    user_id: Optional[str] = None
    address: AddressSnapshot
    items: list[OrderItem] = Field(..., min_length=1)
    subtotal: float = Field(0.0, ge=0)
    discount: float = Field(0.0, ge=0)
    shipping_fee: float = Field(0.0, ge=0)
    total_amount: Optional[float] = None
    coupon_code: Optional[str] = None
    coupon: Optional[CouponSnapshot] = None
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.UNPAID
    payment_method: PaymentMethod
    placed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Settings:
        name = "orders"
        indexes = [
            "user_id",
            "status",
            "payment_status",
            "placed_at",
        ]


class Payment(Document):
    order_id: PydanticObjectId
    user_id: Optional[PydanticObjectId] = None
    gateway: PaymentMethod
    gateway_order_id: Optional[str] = None
    transaction_id: Optional[str] = None
    gateway_signature: Optional[str] = None
    amount: float = Field(..., gt=0)
    currency: str = "INR"
    status: PaymentGatewayStatus = PaymentGatewayStatus.INITIATED
    refund_id: Optional[str] = None
    refund_amount: Optional[float] = None
    refunded_at: Optional[datetime] = None
    initiated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    paid_at: Optional[datetime] = None

    class Settings:
        name = "payments"
        indexes = [
            "order_id",
            "transaction_id",
            "status",
        ]


class Coupon(Document):
    code: str = Field(..., unique=True)
    type: CouponType
    value: float = Field(..., gt=0)
    min_order_amount: float = Field(0.0, ge=0)
    max_discount: Optional[float] = None
    is_active: bool = True
    usage_limit: Optional[int] = None
    used_count: int = 0
    valid_from: datetime
    valid_until: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "coupons"
        indexes = ["code", "is_active", "valid_until"]


# ---------------------------------------------------------------------------
# PAYMENT
# ---------------------------------------------------------------------------


class Payment(Document):
    order_id: Annotated[PydanticObjectId, Indexed()]
    user_id: Annotated[Optional[PydanticObjectId], Indexed()] = None  # ✅ Optional karo

    gateway: PaymentMethod
    gateway_order_id: Optional[str] = None
    transaction_id: Optional[str] = None
    gateway_signature: Optional[str] = None

    amount: float = Field(..., gt=0)
    currency: str = "INR"

    status: PaymentGatewayStatus = PaymentGatewayStatus.INITIATED

    refund_id: Optional[str] = None
    refund_amount: Optional[float] = None
    refunded_at: Optional[datetime] = None

    initiated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    paid_at: Optional[datetime] = None

    class Settings:
        name = "payments"
        indexes = [
            "order_id",
            "transaction_id",
            "status",
        ]


# ---------------------------------------------------------------------------
# COUPON
# ---------------------------------------------------------------------------


class Coupon(Document):
    code: Annotated[str, Indexed(unique=True)]
    type: CouponType

    value: float = Field(..., gt=0)
    min_order_amount: float = Field(0.0, ge=0)
    max_discount: Optional[float] = None

    is_active: bool = True
    usage_limit: Optional[int] = None
    used_count: int = 0

    valid_from: datetime
    valid_until: datetime

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "coupons"
        indexes = ["code", "is_active", "valid_until"]
