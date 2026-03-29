from config.db import coupon_collection
from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId


async def createCouponServices(data, userId):
    coupon = await coupon_collection.find_one({"code": data.code})
    if coupon:
        raise HTTPException(status_code=400, detail="Coupon already exists")

    if data.valid_until < data.valid_from:
        raise HTTPException(
            status_code=400, detail="valid_until must be after valid_from"
        )

    coupon_data = data.model_dump()
    result = await coupon_collection.insert_one(coupon_data)
    document = await coupon_collection.find_one({"_id": result.inserted_id})
    document["_id"] = str(document["_id"])

    return {"msg": "Coupon created successfully", "data": document}


async def verifyCouponService(coupon_code, subtotal):
    coupon = await coupon_collection.find_one({"code": coupon_code})
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon does not exist")

    if not coupon["is_active"]:
        raise HTTPException(status_code=400, detail="Coupon is not active")

    if (
        coupon["usage_limit"] is not None
        and coupon["used_count"] >= coupon["usage_limit"]
    ):
        raise HTTPException(status_code=400, detail="Coupon limit reached")

    if coupon["valid_until"] < datetime.now():
        raise HTTPException(status_code=400, detail="Coupon is expired")

    if subtotal < coupon["min_order_amount"]:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum order amount is {coupon['min_order_amount']}",
        )

    # ✅ discount calculate karo
    if coupon["type"] == "flat":
        discount = coupon["value"]
    else:  # percentage
        discount = subtotal * (coupon["value"] / 100)
        if coupon["max_discount"]:
            discount = min(discount, coupon["max_discount"])  # cap lagao

    return {
        "coupon_id": str(coupon["_id"]),
        "code": coupon["code"],
        "type": coupon["type"],
        "value": coupon["value"],
        "discount_amount": discount,
    }


async def deleteCouponServices(data):
    coupon = await coupon_collection.find_one_and_delete({"_id": ObjectId(data.id)})

    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")

    return {"msg": "Coupon deleted successfully"}
