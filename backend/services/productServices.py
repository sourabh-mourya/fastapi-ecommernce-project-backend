from config.db import product_collection
from fastapi import HTTPException
from bson import ObjectId


async def productServices(data, userId):
    productData = data.model_dump()
    productData["admin_id"] = userId
    result = await product_collection.insert_one(productData)
    document = await product_collection.find_one({"_id": result.inserted_id})
    document["_id"] = str(document["_id"])
    return {"msg": "Product added successfully", "data": document}


async def getProductServices(page: int = 1, limit: int = 10, sort: str = "created_at"):
    skip = (page - 1) * limit
    direction = -1 if sort.startswith("-") else 1
    sort_field = sort.lstrip("-")

    cursor = (
        product_collection.find()
        .sort(sort_field, direction)
        .skip(skip)
        .limit(limit)  # ye cursor return ye db se data ko fetch nhi krta hi
    )
    products = await cursor.to_list(length=None)  # acutal db se data ye fetch krta hi

    if len(products) == 0:
        raise HTTPException(status_code=404, detail="No Products")

    for p in products:
        p["_id"] = str(p["_id"])

    total = await product_collection.count_documents({})

    return {
        "msg": "All products are available",
        "data": products,
        "page": page,
        "limit": limit,
        "total": total,
    }


async def getSingleProductServices(id: str):
    product = await product_collection.find_one({"_id": ObjectId(id)})

    if not product:
        raise HTTPException(404, detail="Product not found")

    product["_id"] = str(product["_id"])

    return {"data": product, "msg": "Product fetched successfully"}


async def updateProductServices(data, id: str, userId):
    product = await product_collection.find_one({"_id": ObjectId(id)})

    if not product:
        raise HTTPException(404, detail="Product not found")

    updated = data.model_dump(exclude_unset=True)
    updated["admin_id"] = userId
    await product_collection.update_one(
        {"_id": ObjectId(id)},  # Bug 1 fix — do alag arguments, ek dict nahi
        {"$set": updated},
    )

    product = await product_collection.find_one(
        {"_id": ObjectId(id)}
    )  # Bug 2 fix — updated data fetch karo
    product["_id"] = str(product["_id"])

    return {"msg": "Product updated successfully", "data": product}


async def deleteProductServices(id: str):
    product = await product_collection.find_one({"_id": ObjectId(id)})

    if not product:
        raise HTTPException(404, detail="Product not found")

    result = await product_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(500, detail="Delete failed")
    return {"msg": "Product delete successfully"}
