from config.db import user_collection
from models.authModel import RegisterUser, LoginUser
from config.Env import EnvConfig
from fastapi import status, HTTPException
from bson import ObjectId
from dotenv import load_dotenv  # ← load_env nahi
import bcrypt
import jwt


async def registerService(data: RegisterUser):
    existingUser = await user_collection.find_one({"email": data.email})
    if existingUser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists with this email",
        )

    genSalt = bcrypt.gensalt(10)
    hashPassword = bcrypt.hashpw(data.password.encode("utf-8"), genSalt)

    userData = data.model_dump()
    userData["password"] = hashPassword.decode("utf-8")

    result = await user_collection.insert_one(userData)

    document = await user_collection.find_one(
        {"_id": result.inserted_id}, {"password": 0}
    )
    document["_id"] = str(document["_id"])
    return {"message": "User created successfully", "data": document}


async def loginService(data: LoginUser):

    existingUser = await user_collection.find_one({"email": data.email})
    if not existingUser:  # ← not lagaya
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist with this email",
        )

    check_password = bcrypt.checkpw(
        data.password.encode(), existingUser["password"].encode()
    )

    if not check_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    token_payload = {
        "_id": str(existingUser["_id"]),
        "role": existingUser["role"],
        "email": existingUser["email"],
    }

    token = jwt.encode(token_payload, EnvConfig.JWT_AUTH, algorithm="HS256")

    # response ke liye _id str karo aur password hatao
    existingUser["_id"] = str(existingUser["_id"])
    del existingUser["password"]  # ← password response mein nahi aana chahiye

    return {"msg": "Login successfully", "token": token, "data": existingUser}


async def profileService(data: dict):
    user_details = await user_collection.find_one({"_id": ObjectId(data["_id"])})
    if not user_details:
        raise HTTPException(status_code=401, detail="User does not exists")

    user_details["_id"] = str(user_details["_id"])  # ← wapas string karo

    return {"msg": "User details", "data": user_details}
