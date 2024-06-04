from typing import List, Optional
from pydantic import BaseModel


# Base models for the API inputs

class ProductBase(BaseModel):
    name: str
    price: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True

class CustomerBase(BaseModel):
    name: str
    phone: str
    address: str
    coupon_code: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int

    class Config:
        orm_mode = True

class CartItem(BaseModel):
    product_id: int
    quantity: int

class Cart(BaseModel):
    customer_id: int
    items: List[CartItem] = []
    coupon_code: Optional[str] = None
    total_value: float = 0

class CouponCode(BaseModel):
    coupon_code: str

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    customer_id: int
    coupon_code: Optional[str] = None
    items: List[OrderItemCreate] = []

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    items: List[OrderItem]

    class Config:
        orm_mode = True
