from config.db import order_collection, product_collection, coupon_collection
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException
from services.couponServices import verifyCouponService


def serialize_doc(doc):
    if isinstance(doc, dict):
        return {key: serialize_doc(value) for key, value in doc.items()}
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    return doc


async def createOrderServices(data):
    
    OrderData = data.model_dump()
    #OrderData["user_id"] = adminId login krke id le lena ab token ke through  

    # ✅ product check karo
    for product in OrderData["items"]:
        db_product = await product_collection.find_one(
            {"_id": ObjectId(str(product["product_id"]))}
        )
        if not db_product:
            raise HTTPException(status_code=404, detail="Product does not exist")
        if db_product["price"] != product["unit_price"]:
            raise HTTPException(status_code=400, detail="Invalid price")
        if db_product["stock"] < product["quantity"]:
            raise HTTPException(status_code=400, detail=f"Only {db_product['stock']} quantity left")

    # ✅ subtotal calculate karo
    subtotal = sum(item["quantity"] * item["unit_price"] for item in OrderData["items"])

    # ✅ coupon apply karo
    discount = 0
    coupon_code = OrderData.get("coupon_code")
    if coupon_code:
        coupon = await verifyCouponService(coupon_code, subtotal)
        discount = coupon["discount_amount"]
        OrderData["coupon"] = coupon

    # ✅ totals set karo
    OrderData["subtotal"] = subtotal
    OrderData["discount"] = discount
    OrderData["total_amount"] = round(subtotal - discount + OrderData["shipping_fee"], 2)

    # ✅ order save karo
    result = await order_collection.insert_one(OrderData)

    # ✅ coupon used_count +1 karo
    if coupon_code:
        await coupon_collection.update_one(
            {"code": coupon_code},
            {"$inc": {"used_count": 1}}
        )

    for product in OrderData["items"]:
        await product_collection.update_one(
            {"_id": ObjectId(str(product["product_id"]))},
            {"$inc": {"stock": -product["quantity"]}}
        )

    document = await order_collection.find_one({"_id": result.inserted_id})
    document = serialize_doc(document)

    return {"msg": "Order created successfully", "data": document}