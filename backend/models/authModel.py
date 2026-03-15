from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    buyer = "buyer"


class User(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6)
    role: UserRole = Field(default=UserRole.buyer)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("name")
    def validate_name(cls, value):
        if len(value) < 3:
            raise ValueError("Name must be greater than 3 characters")
        return value

class RegisterUser(User):
    pass #mtlb apne ko saari fields chiye 

class LoginUser(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6)
    