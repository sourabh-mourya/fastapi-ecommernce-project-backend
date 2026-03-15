from services.productServices import (
    productServices,
    getProductServices,
    getSingleProductServices,
    updateProductServices,
    deleteProductServices
)


async def productController(data, userId):
    res_obj = await productServices(data, userId)
    return res_obj


async def getProductController(page, limit, sort):
    res_obj = await getProductServices(page, limit, sort)
    return res_obj


async def getSingleProductController(id: str):
    res_obj = await getSingleProductServices(id)
    return res_obj


async def updateProductController(data, id: str, userId):
    res_obj = await updateProductServices(data,id, userId)
    return res_obj


async def deleteProductController(id:str):
    res_obj = await deleteProductServices(id)
    return res_obj
