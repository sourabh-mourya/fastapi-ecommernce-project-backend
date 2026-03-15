from services.authServices import registerService, loginService,profileService
from models.authModel import RegisterUser, LoginUser


async def registerController(data: RegisterUser):
    res_obj = await registerService(data)
    return res_obj


async def loginController(data: LoginUser):
    res_obj = await loginService(data)
    return res_obj

async def profileController(data:dict):
    res_obj=await profileService(data)
    return  res_obj