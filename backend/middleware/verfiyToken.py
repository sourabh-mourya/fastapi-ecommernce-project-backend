from fastapi import Request, HTTPException
from config.db import EnvConfig
import jwt


def verifyToken(req: Request):
    authorization = req.headers.get("Authorization", "")

    if not authorization or not authorization.startswith("Bearer "):  # ← space add kiya
        raise HTTPException(status_code=401, detail="Please login first")

    token = authorization.split(" ")[1]  # ← " " space se split karo

    if not token:
        raise HTTPException(status_code=401, detail="Please provide valid token")

    try:
        payload = jwt.decode(
            token, EnvConfig.JWT_AUTH, algorithms=["HS256"]  # ← algorithms fix kiya
        )
        return payload  # ← poora dict return karo, sirf _id nahi
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired, please login again")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
    except Exception as e:
        raise HTTPException(401, f"{e}")
