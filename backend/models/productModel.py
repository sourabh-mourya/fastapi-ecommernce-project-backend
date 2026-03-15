from pydantic import BaseModel, Field
from config.db import db
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ProductCategory(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    furniture = "furniture"
    food = "food"
    books = "books"
    other = "other"


class ProductStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    out_of_stock = "out_of_stock"


class Product(BaseModel):
    # Basic Info
    name: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    price: float = Field(..., gt=0)                        # gt=0 matlab price 0 se zyada ho
    discount_price: Optional[float] = Field(default=None)  # sale price
    
    # Category & Status
    category: ProductCategory = Field(default=ProductCategory.other)
    status: ProductStatus = Field(default=ProductStatus.active)
    
    # Stock
    stock: int = Field(..., ge=0)                          # ge=0 matlab 0 ya zyada
    
    # Images
    images: List[str] = Field(default=[])                  # image URLs ki list
    thumbnail: Optional[str] = Field(default=None)         # main image
    
    # Seller
    admin_id: Optional[str] = Field(default=None)

    # Extra
    tags: List[str] = Field(default=[])                    # search ke liye
    ratings: float = Field(default=0.0)                    # average rating
    total_reviews: int = Field(default=0)                  # kitne reviews hain

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CreateProduct(Product):
    pass  # saari fields chahiye


class UpdateProduct(BaseModel):
    # Update mein sab optional hoga
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    category: Optional[ProductCategory] = None
    status: Optional[ProductStatus] = None
    stock: Optional[int] = None
    images: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    tags: Optional[List[str]] = None
    
    
