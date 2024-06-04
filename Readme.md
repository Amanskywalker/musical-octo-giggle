# E-commerce Store API

This repository is based on the Question Statement mentioned in the `Question_Statement` file. The application is built using FastAPI and provides functionality for managing products, customers, orders, and carts in an e-commerce store.

## Technologies Used

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
- **Uvicorn**: An ASGI server for running FastAPI applications.
- **Pytest**: A framework for unit testing.

## Features

- Product Management
- Customer Management
- Cart Management
- Order Placement with Coupon Code Application
- Admin APIs for Generating Discount Codes and Listing Purchase Statistics

## How to Execute

### Prerequisites

- Install `pipenv`:
    ```sh
    pip3 install pipenv
    ```

### Setup

1. Install Dependencies:
    ```sh 
    pipenv install
    ```

2. Activate Virtual Environment:

    ```sh
    pipenv shell
    ```

### Running the Server

1. Run the Debugging Server:

    ```sh
    pipenv run uvicorn app.main:app --reload
    ```
    The application will be available at http://localhost:8000.

### Running the Tests

1. Execute Test Cases:

    ```sh
    pipenv run pytest
    ```

## Endpoints

### Public APIs

- GET `/products/`: List all products.
- GET `/products/{product_id}`: Get details of a specific product.
- POST `/products/`: Create a new product.
- GET `/customers/`: List all customers.
- GET `/customers/{customer_id}`: Get details of a specific customer.
- POST `/customers/`: Create a new customer.
- POST `/cart/add/`: Add an item to the cart.
- DELETE `/cart/remove/{product_id}/`: Remove an item from the cart.
- POST `/cart/apply-coupon/`: Apply a coupon to the cart.
- GET `/cart/`: View the cart.
- POST `/orders/`: Place an order.

### Admin APIs

- POST `/admin/generate-discount-code/`: Generate a discount code by the admin.
- GET `/admin/purchase-stats/`: List count of items purchased, total purchase amount, list of discount codes, and total discount amount.

## Improvements

Which can be added to this project

- **Authentication and Authorization**: As its a demo project, to make it more secure, user authentication and authorization can be added.

- **Database Integration**: As its a demo project, its used in-memory data structure, we can integrate it with a database for persistent storage.

- **Comprehensive Error Handling**: As its a demo project, we can enhance error handling and validation across all endpoints.