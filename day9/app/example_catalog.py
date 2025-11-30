import json
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDERS_FILE = ROOT / "day9_orders.json"

PRODUCTS = [
    {"id": "mug-001", "name": "Stoneware Coffee Mug", "description": "350ml ceramic mug", "price": 800, "currency": "INR", "category": "mug", "color": "white"},
    {"id": "mug-002", "name": "Blue Coffee Mug", "description": "Ceramic mug - blue", "price": 850, "currency": "INR", "category": "mug", "color": "blue"},
    {"id": "tee-001", "name": "Logo T-Shirt", "description": "Cotton T-Shirt", "price": 699, "currency": "INR", "category": "tshirt", "color": "black", "sizes": ["S","M","L","XL"]},
    {"id": "hoodie-001", "name": "Comfy Hoodie", "description": "Warm hoodie", "price": 1499, "currency": "INR", "category": "hoodie", "color": "black", "sizes": ["M","L"]},
    {"id": "hoodie-002", "name": "Grey Hoodie", "description": "Classic hoodie", "price": 1299, "currency": "INR", "category": "hoodie", "color": "grey", "sizes": ["S","M","L"]},
    {"id": "cap-001", "name": "Baseball Cap", "description": "Adjustable cap", "price": 399, "currency": "INR", "category": "cap", "color": "black"}
]

def list_products(filters=None):
    if not filters:
        return PRODUCTS.copy()

    results = PRODUCTS
    f = filters

    def keep(p):
        if "category" in f and f["category"] and p["category"] != f["category"]:
            return False
        if "color" in f and f["color"] and p.get("color") != f["color"]:
            return False
        if "max_price" in f and f["max_price"] and p["price"] > f["max_price"]:
            return False
        if "size" in f and f["size"]:
            sizes = p.get("sizes")
            if not sizes or f["size"] not in sizes:
                return False
        return True

    return [p.copy() for p in results if keep(p)]

def _load_orders():
    if not ORDERS_FILE.exists():
        return []
    try:
        return json.loads(ORDERS_FILE.read_text())
    except:
        return []

def _save_orders(orders):
    ORDERS_FILE.write_text(json.dumps(orders, indent=2))

def create_order(line_items, currency="INR"):
    orders = _load_orders()
    items = []
    total = 0

    for li in line_items:
        pid = li["product_id"]
        qty = li.get("quantity",1)

        prod = next((p for p in PRODUCTS if p["id"] == pid), None)
        if not prod:
            raise ValueError("Product not found: " + pid)

        line_total = prod["price"] * qty
        total += line_total

        items.append({
            "product_id": pid,
            "name": prod["name"],
            "quantity": qty,
            "unit_amount": prod["price"],
            "currency": currency,
            "line_total": line_total
        })

    order = {
        "id": str(uuid.uuid4())[:8],
        "items": items,
        "total": total,
        "currency": currency,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    orders.append(order)
    _save_orders(orders)
    return order

def last_order():
    orders = _load_orders()
    return orders[-1] if orders else None
