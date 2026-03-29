from fastapi import APIRouter, Depends
from models.couponModel import Coupon
from routes.authRoute import requireRole
from controllers.couponController import createCouponController, deleteCouponController

router = APIRouter(prefix='/api/v1/coupon', tags=['coupon'])

@router.post('/create_coupon')
async def createCoupon(data: Coupon, user=Depends(requireRole('admin'))):
    userId = str(user['_id'])
    print('j')
    return await createCouponController(data, userId)

@router.delete('/delete_coupon/{coupon_id}')
async def deleteCoupon(coupon_id: str, user=Depends(requireRole('admin'))):
    return await deleteCouponController(coupon_id)