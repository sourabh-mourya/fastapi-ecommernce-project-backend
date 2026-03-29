from config.db import order_collection, payment_collection
from config.Env import EnvConfig
from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from config.razorpayConfig import razorpayInstance
import hmac
import hashlib

async def initiatePaymentServices(data, userId):
    order = await order_collection.find_one({"_id": ObjectId(data.order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order does not exist")

    options = {
        "amount": int(order["total_amount"] * 100),
        "currency": "INR",
        "receipt": f"receipt_{order['_id']}_{userId}_{datetime.now().timestamp()}",
        "notes": {
            "order_id": str(order["_id"]),  # ✅ string key chahiye
            "user_id": userId,
            "items": str(
                [item["product_name"] for item in order["items"]]
            ),  # ✅ list nahi, string
        },
    }

    # ✅ razorpay async nahi hai — await mat lagao
    razorpay_order = razorpayInstance.order.create(options)

    # ✅ payment DB mein save karo
    await payment_collection.insert_one(
        {
            "order_id": ObjectId(data.order_id),
            "user_id": ObjectId(userId),
            "gateway": "razorpay",
            "razorpay_order_id": razorpay_order["id"],
            "amount": order["total_amount"],
            "currency": "INR",
            "status": "initiated",
            "initiated_at": datetime.now(timezone.utc),
        }
    )

    return {
        "razorpay_order_id": razorpay_order["id"],
        "amount": order["total_amount"],
        "currency": "INR",
    }




async def verifyPaymentServices(data):
    # ✅ signature verify karo
    secret = EnvConfig.RAZORPAY_KEY_SECRET
    
    body = f"{data.razorpay_order_id}|{data.razorpay_payment_id}"
    
    generated_signature = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if generated_signature != data.razorpay_signature:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    
    # ✅ order update karo
    await order_collection.update_one(
        {"_id": ObjectId(data.order_id)},
        {"$set": {
            "status": "confirmed",
            "payment_status": "paid",
            "confirmed_at": datetime.now(timezone.utc)
        }}
    )
    
    # ✅ payment record update karo
    await payment_collection.update_one(
        {"razorpay_order_id": data.razorpay_order_id},
        {"$set": {
            "transaction_id": data.razorpay_payment_id,
            "gateway_signature": data.razorpay_signature,
            "status": "success",
            "paid_at": datetime.now(timezone.utc)
        }}
    )
    
    return {"msg": "Payment verified successfully"}



async def refundPaymentServices(data, userId):
    # ✅ payment check karo
    payment = await payment_collection.find_one({
        "order_id": ObjectId(data.order_id)
    })
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # ✅ already refunded?
    if payment["status"] == "refunded":
        raise HTTPException(status_code=400, detail="Payment already refunded")

    # ✅ payment successful thi?
    if payment["status"] != "success":
        raise HTTPException(status_code=400, detail="Payment not successful yet")

    # ✅ razorpay pe refund karo
    refund = razorpayInstance.payment.refund(
        payment["transaction_id"],
        {
            "amount": int(payment["amount"] * 100),  # paise mein
            "speed": "normal",
            "notes": {
                "order_id": str(data.order_id),
                "user_id": str(userId)
            }
        }
    )

    # ✅ payment record update karo
    await payment_collection.update_one(
        {"order_id": ObjectId(data.order_id)},
        {"$set": {
            "status": "refunded",
            "refund_id": refund["id"],
            "refund_amount": payment["amount"],
            "refunded_at": datetime.now(timezone.utc)
        }}
    )

    # ✅ order update karo
    await order_collection.update_one(
        {"_id": ObjectId(data.order_id)},
        {"$set": {
            "status": "cancelled",
            "payment_status": "refunded",
            "cancelled_at": datetime.now(timezone.utc)
        }}
    )

    return {"msg": "Refund successful", "refund_id": refund["id"]}