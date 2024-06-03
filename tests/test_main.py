import pytest
from fastapi.testclient import TestClient
from app import app
from app.models import Product, Customer, CartItem
import app.crud as crud

client = TestClient(app)

# data setup
def setup_module(module):
    global products, customers, order_count, n
    crud.products = {
        1: Product(id=1, name="Product 1", price=10.0),
        2: Product(id=2, name="Product 2", price=15.0)
    }
    crud.customers = {
        1: Customer(id=1, name="Customer 1", phone="1234567890", address="123 Main St", email="customer1@example.com")
    }
    crud.order_count[1] = 0

def test_add_item_to_cart():
    response = client.post("/cart/add/?customer_id=1", json={"product_id": 1, "quantity": 2})
    assert response.status_code == 200
    assert response.json() == {"message": "Item added to cart"}

    response = client.get("/cart/?customer_id=1")
    assert response.status_code == 200
    cart = response.json()
    assert len(cart["items"]) == 1
    assert cart["items"][0]["product_id"] == 1
    assert cart["items"][0]["quantity"] == 2
    assert cart["items"][0]["price"] == 10.0
    assert cart["total_value"] == 20.0

def test_remove_item_from_cart():
    # reduce the item count by 1
    response = client.delete("/cart/remove/1/?customer_id=1")
    assert response.status_code == 200
    assert response.json() == {"message": "Item removed from cart"}

    # again reduce the item count by 1
    response = client.delete("/cart/remove/1/?customer_id=1")
    assert response.status_code == 200
    assert response.json() == {"message": "Item removed from cart"}

    # as item is deleted from the cart, cart should be empty now
    response = client.get("/cart/?customer_id=1")
    assert response.status_code == 200
    cart = response.json()
    assert len(cart["items"]) == 0
    assert cart["total_value"] == 0

def test_place_order_without_coupon():
    # add item to cart
    client.post("/cart/add/?customer_id=1", json={"product_id": 1, "quantity": 2 })

    response = client.post("/orders/?customer_id=1")
    assert response.status_code == 200
    order = response.json()
    assert order["total_value"] == 20.0  # no discount
    assert order["coupon_code"] is None

    response = client.get("/cart/?customer_id=1")
    assert response.status_code == 200
    cart = response.json()
    assert len(cart["items"]) == 0
    assert cart["total_value"] == 0
    assert cart["coupon_code"] is None

def test_apply_coupon_to_cart():
    # add item to cart
    client.post("/cart/add/?customer_id=1", json={"product_id": 1, "quantity": 2 })

    # simualte the coupon generation and assigment
    crud.customers[1].coupon_code = "VALIDCOUPON"

    response = client.post("/cart/apply-coupon/?customer_id=1", json={"coupon_code": "VALIDCOUPON"})
    assert response.status_code == 200
    assert response.json() == {"message": "Coupon applied to cart"}

    response = client.get("/cart/?customer_id=1")
    assert response.status_code == 200
    cart = response.json()
    assert cart["coupon_code"] == "VALIDCOUPON"

def test_place_order_with_valid_coupon():
    # add item to cart
    crud.customers[1].coupon_code = "VALIDCOUPON"
    client.post("/cart/apply-coupon/?customer_id=1", json={"coupon_code": "VALIDCOUPON"})
    client.post("/cart/add/?customer_id=1", json={"product_id": 1, "quantity": 2})

    response = client.post("/orders/?customer_id=1")
    assert response.status_code == 200
    order = response.json()
    assert order["total_value"] == 36  # 10% discount
    assert order["coupon_code"] == "VALIDCOUPON"

    response = client.get("/cart/?customer_id=1")
    assert response.status_code == 200
    cart = response.json()
    assert len(cart["items"]) == 0
    assert cart["total_value"] == 0
    assert cart["coupon_code"] is None

def test_place_order_without_coupon():
    # add item to cart
    client.post("/cart/add/?customer_id=1", json={"product_id": 1, "quantity": 2})

    response = client.post("/orders/?customer_id=1")
    assert response.status_code == 200
    order = response.json()
    assert order["total_value"] == 20.0  # no discount
    assert order["coupon_code"] is None

    response = client.get("/cart/?customer_id=1")
    assert response.status_code == 200
    cart = response.json()
    assert len(cart["items"]) == 0
    assert cart["total_value"] == 0
    assert cart["coupon_code"] is None

def test_generate_discount_code():
    crud.order_count[1] = crud.nth_order # customer order count set to nth_order
    crud.customers[1].coupon_code = None

    response = client.post("/admin/generate-discount-code/?customer_id=1")
    assert response.status_code == 200
    assert response.json() == {"message": "Discount codes generated"}

def test_generate_discount_code_for_n_plus_1_order():
    crud.order_count[1] = crud.nth_order+1 # customer order count set to nth + 1 order
    crud.customers[1].coupon_code = None

    response = client.post("/admin/generate-discount-code/?customer_id=1")
    assert response.status_code == 200
    assert response.json() == {"message": "Discount codes generation failed"}

def test_generate_discount_code_for_existing_coupon_code():
    crud.order_count[1] = crud.nth_order # customer order count set to nth_order
    crud.customers[1].coupon_code = "VALIDCOUPON" # customer has the existing coupon code

    response = client.post("/admin/generate-discount-code/?customer_id=1")
    assert response.status_code == 200
    assert response.json() == {"message": "Discount codes generation failed"}

def test_store_statistics():
    response = client.get("/admin/store-statistics/")
    assert response.status_code == 200
    stats = response.json()
    assert "total_items_purchased" in stats
    assert "total_purchase_amount" in stats
    assert "discount_codes" in stats
    assert "total_discount_amount" in stats