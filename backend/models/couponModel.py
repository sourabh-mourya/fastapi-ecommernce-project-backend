from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class CouponType(str, Enum):
    FLAT = "flat"
    PERCENTAGE = "percentage"

class Coupon(BaseModel):
    code: str = Field(...)
    type: CouponType = CouponType.FLAT
    value: float = Field(..., gt=0)
    min_order_amount: float = Field(0.0, ge=0)
    max_discount: Optional[float] = None
    is_active: bool = True
    usage_limit: Optional[int] = None
    used_count: int = 0
    valid_from: datetime        # ✅ add karo
    valid_until: datetime
