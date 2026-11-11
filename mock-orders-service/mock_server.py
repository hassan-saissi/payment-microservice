from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Dict
from copy import deepcopy

app = FastAPI(
    title="Mock Orders Service",
    description="Simulates the Orders Microservice",
    version="1.0.0"
)

# --------------------------------
# 1. Fake database
# --------------------------------

INITIAL_ORDERS = {
    "ORD-001": {
        "id": "ORD-001",
        "status": "PENDING_PAYMENT"
    },
    "ORD-002": {
        "id": "ORD-002",
        "status": "PAID"
    },
    "ORD-003": {
        "id": "ORD-003",
        "status": "CANCELLED"
    },
    "ORD-004": {
        "id": "ORD-004",
        "status": "PROCESSING"
    },
    "ORD-005": {
        "id": "ORD-005",
        "status": "PENDING_PAYMENT"
    }
}

orders: Dict[str, dict] = deepcopy(INITIAL_ORDERS)

# Simulate PATCH failure for this order
PATCH_FAILURE_IDS = {"ORD-005"}


# --------------------------------
# 2. Request models
# --------------------------------

class OrderStatusUpdate(BaseModel):
    status: str


# --------------------------------
# 3. GET an order
# GET /api/orders/{order_id}
# --------------------------------

@app.get("/api/orders/{order_id}")
def get_order(order_id: str):

    order = orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


# --------------------------------
# 4. PATCH order status
# PATCH /api/orders/{order_id}/status
# --------------------------------

@app.patch("/api/orders/{order_id}/status")
def update_order_status(
    order_id: str,
    payload: OrderStatusUpdate
):

    order = orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Simulate an internal server error
    if order_id in PATCH_FAILURE_IDS:
        raise HTTPException(
            status_code=500,
            detail="Simulated Orders Service failure"
        )

    order["status"] = payload.status

    return Response(status_code=204)


# --------------------------------
# 5. Inspect fake database
# --------------------------------

@app.get("/__mock/orders")
def get_all_mock_orders():
    return list(orders.values())


# --------------------------------
# 6. Reset fake database
# --------------------------------

@app.post("/__mock/reset")
def reset_mock_database():

    global orders

    orders = deepcopy(INITIAL_ORDERS)

    return {
        "message": "Mock database reset successfully",
        "orders": list(orders.values())
    }


# --------------------------------
# 7. Health check
# --------------------------------

@app.get("/health")
def health_check():
    return {
        "service": "Mock Orders Service",
        "status": "UP"
    }