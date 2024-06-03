from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app import schemas, crud
from app.models import CartItem

router = APIRouter()

@router.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 10):
    return crud.get_products(skip=skip, limit=limit)

@router.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int):
    product = crud.get_product(product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate):
    return crud.create_product(product=product)

@router.get("/customers/", response_model=List[schemas.Customer])
def read_customers(skip: int = 0, limit: int = 10):
    return crud.get_customers(skip=skip, limit=limit)

@router.get("/customers/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int):
    customer = crud.get_customer(customer_id=customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate):
    return crud.create_customer(customer=customer)

@router.post("/cart/add/")
def add_item_to_cart(customer_id: int, item: schemas.CartItem):
    crud.add_to_cart(customer_id, item)
    return {"message": "Item added to cart"}

@router.delete("/cart/remove/{product_id}/")
def remove_item_from_cart(customer_id: int, product_id: int):
    crud.remove_from_cart(customer_id, product_id)
    return {"message": "Item removed from cart"}

@router.post("/cart/apply-coupon/")
def apply_coupon(customer_id: int, coupon_code : schemas.CouponCode):
    print("AC", customer_id, coupon_code)
    crud.apply_coupon_to_cart(customer_id, coupon_code.coupon_code)
    return {"message": "Coupon applied to cart"}

@router.get("/cart/")
def view_cart(customer_id: int):
    return crud.get_cart(customer_id)

@router.get("/orders/", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 10):
    return crud.get_orders(skip=skip, limit=limit)

@router.get("/orders/{order_id}", response_model=schemas.Order)
def read_order(order_id: int):
    order = crud.get_order(order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/orders/")
def place_order(customer_id: int):
    return crud.create_order(customer_id)

# admin functions
@router.post("/admin/generate-discount-code/")
def generate_discount_code(customer_id: int):
    result = crud.admin_generate_discount_code(customer_id)
    if result:
        return {"message": "Discount codes generated"}
    else:
        return {"message": "Discount codes generation failed"}

@router.get("/admin/store-statistics/")
def store_statistics():
    return crud.get_store_statistics()