import random
import string
from app.models import Product, Customer, Cart, CartItem, Order, OrderItem
from app.schemas import ProductCreate, CustomerCreate, OrderCreate

# In-memory stores
products = {}
customers = {}
customer_carts = {}
orders = {}
order_count = 0
nth_order = 5  # nth order

def get_next_id(store):
    return max(store.keys(), default=0) + 1

def create_product(product: ProductCreate):
    product_id = get_next_id(products)
    new_product = Product(id=product_id, **product.dict())
    products[product_id] = new_product
    return new_product

def create_customer(customer: CustomerCreate):
    customer_id = get_next_id(customers)
    new_customer = Customer(id=customer_id, **customer.dict())
    customers[customer_id] = new_customer
    return new_customer

def update_cart_total(cart: Cart):
    cart.total_value = sum(item.quantity * item.price for item in cart.items)

def add_to_cart(customer_id: int, item: CartItem):
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_cart = customer_carts.get(customer_id, Cart(customer_id=customer_id))
    
    # item in the cart
    for cart_item in customer_cart.items:
        if cart_item.product_id == item.product_id:
            cart_item.quantity += item.quantity
            cart_item.price = products[cart_item.product_id].price
            break
    # item not in the cart
    else:
        item_temp = CartItem(
            product_id = item.product_id,
            quantity = item.quantity,
            price = products[item.product_id].price
        )
        customer_cart.items.append(item_temp)
    
    update_cart_total(customer_cart)
    customer_carts[customer_id] = customer_cart
    print("add : ",customer_carts)

def remove_from_cart(customer_id: int, product_id: int):
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_cart = customer_carts.get(customer_id)
    if not customer_cart:
        return
    
    for cart_item in customer_cart.items:
        if cart_item.product_id == product_id:
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                customer_cart.items.remove(cart_item)
            break
    
    update_cart_total(customer_cart)
    customer_carts[customer_id] = customer_cart
    print("remove", customer_carts)

def clear_cart(customer_id: int):
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_cart = customer_carts.get(customer_id)
    if customer_cart:
        customer_cart.items.clear()
        customer_cart.coupon_code = None
        customer_cart.total_value = 0
        customer_carts[customer_id] = customer_cart

def get_cart(customer_id: int):
    customer_cart = customer_carts.get(customer_id, Cart(customer_id=customer_id))
    return customer_cart

def apply_coupon_to_cart(customer_id: int, coupon_code):
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")

    print("AC", customer_id, coupon_code)

    customer = customers[customer_id]
    if customer.coupon_code == coupon_code:
        customer_cart = customer_carts.get(customer_id)
        if customer_cart:
            customer_cart.coupon_code = coupon_code
            customer_carts[customer_id] = customer_cart
        return 
    
    raise HTTPException(status_code=400, detail="Invalid coupon code")

def generate_coupon_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def send_coupon_email(customer: Customer, coupon_code: str):
    # simulate sending an email
    print(f"Sending email to {customer.email} with coupon code: {coupon_code}")

def create_order(customer_id):
    global order_count
    order_count += 1
    order_id = get_next_id(orders)

    customer_cart = customer_carts.get(customer_id)    
    print("o1 here", customer_cart)

    # convert items in the cart into order items
    order_items = []
    for cart_item in customer_cart.items:
        order_item = OrderItem(product_id=cart_item.product_id, quantity=cart_item.quantity, price=cart_item.price)
        order_items.append(order_item)
    
    customer = customers[customer_id]
    
    print("o2 here", order_items, customer)

    order_total_value = customer_cart.total_value
    order_coupon_code = None

    # Apply the coupon code if it's valid and applied on the cart
    if customer_cart.coupon_code and customer_cart.coupon_code == customer.coupon_code:
        order_total_value = customer_cart.total_value * 0.9  # 10% discount
        order_coupon_code = customer_cart.coupon_code
        customer.coupon_code = None  # clear the coupon code after use

    new_order = Order(id=order_id, customer_id=customer_id, total_value=order_total_value,
                      coupon_code=order_coupon_code, items=order_items)
    
    # generate a new coupon code for each nth order
    if order_count % nth_order == 0:
        coupon_code = generate_coupon_code()
        customer.coupon_code = coupon_code
        send_coupon_email(customer, coupon_code)

    orders[order_id] = new_order
    
    # clear the cart after converting it into an order
    clear_cart(customer_id)
    
    print("order", new_order)
    return new_order

def get_product(product_id: int):
    return products.get(product_id)

def get_customer(customer_id: int):
    return customers.get(customer_id)

def get_order(order_id: int):
    return orders.get(order_id)

def get_products(skip: int = 0, limit: int = 10):
    return list(products.values())[skip:skip+limit]

def get_customers(skip: int = 0, limit: int = 10):
    return list(customers.values())[skip:skip+limit]

def get_orders(skip: int = 0, limit: int = 10):
    return list(orders.values())[skip:skip+limit]
