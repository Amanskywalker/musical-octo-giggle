from typing import List, Optional
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float

class Customer(BaseModel):
    id: int
    name: str
    phone: str
    address: str
    email: str
    coupon_code: Optional[str] = None

class CartItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class Cart(BaseModel):
    customer_id: int
    items: List[CartItem] = []
    coupon_code: Optional[str] = None
    total_value: float = 0

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class Order(BaseModel):
    id: int
    customer_id: int
    total_value: float
    coupon_code: Optional[str] = None
    items: List[OrderItem]
