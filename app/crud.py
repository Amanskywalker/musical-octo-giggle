import random
import string
from app.models import Product, Customer, Cart, CartItem, Order, OrderItem
from app.schemas import ProductCreate, CustomerCreate, OrderCreate

# In-memory stores
products = {}
customers = {}
customer_carts = {}
orders = {}
discount_codes = {}
order_count = {}
nth_order = 5  # nth order

def get_next_id(store):
    '''
        Get the next order id
    '''
    return max(store.keys(), default=0) + 1

def create_product(product: ProductCreate):
    '''
        Create Products
    '''
    product_id = get_next_id(products)
    new_product = Product(id=product_id, **product.dict())
    products[product_id] = new_product
    return new_product

def create_customer(customer: CustomerCreate):
    '''
        Create Customer
    '''
    customer_id = get_next_id(customers)
    new_customer = Customer(id=customer_id, **customer.dict())
    customers[customer_id] = new_customer
    return new_customer

def update_cart_total(cart: Cart):
    '''
        Update the cart total
    '''
    cart.total_value = sum(item.quantity * item.price for item in cart.items)

def add_to_cart(customer_id: int, item: CartItem):
    '''
        Add to cart function
        
        Each customer can have only one cart

        - If product is already present in the cart then its incremented
        - If product doesn't exist in the cart then its added in the cart

    '''
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

def remove_from_cart(customer_id: int, product_id: int):
    '''
        Remove the item from the cart

        - If item it found in the cart then its quantity is decresed
        - if Quantity is 0 then its removed from the cart
    '''

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

def clear_cart(customer_id: int):
    '''
        Clear/Reset the cart
    '''
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_cart = customer_carts.get(customer_id)
    if customer_cart:
        customer_cart.items.clear()
        customer_cart.coupon_code = None
        customer_cart.total_value = 0
        customer_carts[customer_id] = customer_cart

def get_cart(customer_id: int):
    '''
        Get the Cart for the given customer
    '''
    customer_cart = customer_carts.get(customer_id, Cart(customer_id=customer_id))
    return customer_cart

def apply_coupon_to_cart(customer_id: int, coupon_code):
    '''
        Apply Coupon to the Cart
    '''
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer = customers[customer_id]
    if customer.coupon_code == coupon_code:
        customer_cart = customer_carts.get(customer_id)
        if customer_cart:
            customer_cart.coupon_code = coupon_code
            customer_carts[customer_id] = customer_cart
        return 
    
    raise HTTPException(status_code=400, detail="Invalid coupon code")

def generate_coupon_code():
    '''
        Genereate Coupon Code
    '''
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def send_coupon_email(customer: Customer, coupon_code: str):
    '''
        Send Email
    '''
    # simulate sending an email
    print(f"Sending email to {customer.email} with coupon code: {coupon_code}")

def create_order(customer_id):
    '''
        Create Order

        Steps:
        - Firstly its convert the cart items to the order Items
        - If a valid coupon code is present in the cart then 10% discount is applied to the order
        - If its nth Order then the coupon code is generated and stored with the customer data
        - Finally cart is cleared
    '''
    global nth_order

    if customer_id not in order_count:
        order_count[customer_id] = 0

    order_count[customer_id] += 1
    order_id = get_next_id(orders)

    customer_cart = customer_carts.get(customer_id)

    # convert items in the cart into order items
    order_items = []
    for cart_item in customer_cart.items:
        order_item = OrderItem(product_id=cart_item.product_id, quantity=cart_item.quantity, price=cart_item.price)
        order_items.append(order_item)
    
    customer = customers[customer_id]

    order_total_value = customer_cart.total_value
    order_coupon_code = None

    # Apply the coupon code if it's valid and applied on the cart
    if customer_cart.coupon_code and customer_cart.coupon_code == customer.coupon_code:
        order_total_value = customer_cart.total_value * 0.9  # 10% discount
        discount_codes[customer.coupon_code] = customer_cart.total_value * 0.1
        order_coupon_code = customer_cart.coupon_code
        customer.coupon_code = None  # clear the coupon code after use

    new_order = Order(id=order_id, customer_id=customer_id, total_value=order_total_value,
                      coupon_code=order_coupon_code, items=order_items)
    
    # generate a new coupon code for each nth order
    if order_count[customer_id] % nth_order == 0:
        coupon_code = generate_coupon_code()
        customer.coupon_code = coupon_code
        send_coupon_email(customer, coupon_code)

    orders[order_id] = new_order
    
    # clear the cart after converting it into an order
    clear_cart(customer_id)
    
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

def get_store_statistics():
    '''
        Store Statics
    '''
    total_items_purchased = sum(item.quantity for order in orders.values() for item in order.items)
    total_purchase_amount = sum(order.total_value for order in orders.values())
    total_discount_amount = sum(discount_codes.values())
    discount_code_list = list(discount_codes.keys())
    
    return {
        "total_items_purchased": total_items_purchased,
        "total_purchase_amount": total_purchase_amount,
        "discount_codes": discount_code_list,
        "total_discount_amount": total_discount_amount
    }

def admin_generate_discount_code(customer_id):
    '''
        Generate Code by Admin

        Conditions:
        - its Xnth Order where X is whole number
        - Customer doesn't have a coupon code mapped to them 
    '''
    if customer_id in order_count and order_count[customer_id] % nth_order == 0:
        customer = customers[customer_id]
        if customer.coupon_code is None:
            # generate coupon code only if customer didn't have a coupon code
            coupon_code = generate_coupon_code()
            customer.coupon_code = coupon_code
            send_coupon_email(customer, coupon_code)
            return True
    
    return False