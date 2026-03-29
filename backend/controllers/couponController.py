from services.couponServices import createCouponServices, deleteCouponServices  # ✅ import add karo

async def createCouponController(data, userId):
    res_obj = await createCouponServices(data, userId)  
    return res_obj

async def deleteCouponController(coupon_id):  
    res_obj = await deleteCouponServices(coupon_id)  
    return res_obj