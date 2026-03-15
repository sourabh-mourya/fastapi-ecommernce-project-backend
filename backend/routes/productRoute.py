from fastapi import APIRouter, Depends
from middleware.verfiyToken import verifyToken
from models.productModel import CreateProduct, Product, UpdateProduct
from controllers.productController import (
    productController,
    getProductController,
    getSingleProductController,
    updateProductController,
    deleteProductController,
)
from routes.authRoute import requireRole

router = APIRouter(prefix="/api/v1", tags=["Products"])


@router.post("/product")
async def product(data: CreateProduct, user=Depends(requireRole("admin"))):
    # user mein token ka payload hai
    # data mein product info hai
    # admin = user["_id"] set karna hoga service mein
    return await productController(data, user["_id"])  # ← _id pass karo


# get all product tki saare user buy kr ske
@router.get("/products")
async def getProduct(page: int = 1, limit: int = 10, sort: str = "created_at"):
    return await getProductController(page, limit, sort)


@router.get("/products/{id}")
async def getSingleProduct(id: str):
    return await getSingleProductController(id)


@router.patch("/products/{id}")
async def updateProduct(data: UpdateProduct, id: str, user=Depends(requireRole("admin"))):
    return await updateProductController(data, id, user["_id"])


@router.delete("/products/{id}")
async def deleteProduct(id: str, _=Depends(requireRole("admin"))):
    return await deleteProductController(id)
