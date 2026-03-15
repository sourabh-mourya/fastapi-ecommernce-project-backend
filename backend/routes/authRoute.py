from fastapi import APIRouter, Depends, HTTPException
from models.authModel import RegisterUser, LoginUser
from controllers.authController import (
    registerController,
    loginController,
    profileController,
)
from middleware.verfiyToken import verifyToken

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register")
async def registerView(data: RegisterUser):
    return await registerController(data)  # ← .dict() hata diya


@router.post("/login")
async def loginView(data: LoginUser):
    return await loginController(data)  # ← .dict() hata diya


def requireRole(required_role: str):
    async def checkRole(data=Depends(verifyToken)):
        # print("data :- ", data)
        user_role = data.get("role")
        # print("role :- ", user_role)
        if user_role != required_role:  # Bug fix — dono alag names
            raise HTTPException(403, "Access denied")
        return data

    return checkRole


# Route mein
@router.get("/profile")
async def profileView(data=Depends(requireRole("seller"))):
    #                             ↑
    #                     requireRole pehle call hoga
    #                     requireRole ke andar verifyToken call hoga
    return await profileController(data)
