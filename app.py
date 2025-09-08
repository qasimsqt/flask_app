from flask import Flask, render_template, redirect, url_for, session, request, jsonify
import random
import logging
import os
from datetime import datetime

# --------------------------
# Flask app setup
# --------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecret-change-in-production')

# Product catalog with Pexels images
PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 1000, "image": "https://images.pexels.com/photos/205421/pexels-photo-205421.jpeg?auto=compress&cs=tinysrgb&w=400"},
    {"id": 2, "name": "Phone", "price": 500, "image": "https://images.pexels.com/photos/699122/pexels-photo-699122.jpeg?auto=compress&cs=tinysrgb&w=400"},
    {"id": 3, "name": "Headphones", "price": 200, "image": "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg?auto=compress&cs=tinysrgb&w=400"},
    {"id": 4, "name": "Watch", "price": 350, "image": "https://images.pexels.com/photos/190819/pexels-photo-190819.jpeg?auto=compress&cs=tinysrgb&w=400"},
    {"id": 5, "name": "Camera", "price": 750, "image": "https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=400"},
    {"id": 6, "name": "Chair", "price": 450, "image": "https://images.pexels.com/photos/7862645/pexels-photo-7862645.jpeg?auto=compress&cs=tinysrgb&w=400"},
    {"id": 7, "name": "Mouse", "price": 330, "image": "https://images.pexels.com/photos/2115256/pexels-photo-2115256.jpeg?auto=compress&cs=tinysrgb&w=400"},
    {"id": 8, "name": "Keyboard", "price": 250, "image": "https://images.pexels.com/photos/2115257/pexels-photo-2115257.jpeg?auto=compress&cs=tinysrgb&w=400"},
    {"id": 9, "name": "Monitor", "price": 650, "image": "https://images.pexels.com/photos/777001/pexels-photo-777001.jpeg?auto=compress&cs=tinysrgb&w=400"},
    {"id": 10, "name": "Speaker", "price": 600, "image": "https://images.pexels.com/photos/3394651/pexels-photo-3394651.jpeg?auto=compress&cs=tinysrgb&w=400"},
    {"id": 11, "name": "WiFi Router", "price": 290, "image": "https://images.pexels.com/photos/4219861/pexels-photo-4219861.jpeg?auto=compress&cs=tinysrgb&w=400"},
]

# --------------------------
# Structured logging setup
# --------------------------
os.makedirs('logs', exist_ok=True)
logger = logging.getLogger("payments")
logger.setLevel(logging.INFO)

# Create file handler
fh = logging.FileHandler("logs/payments.log")
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(event_type)s | %(status)s | %(amount)s | %(path)s | %(extra)s'
)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Helper function for structured logs
def log_event(event_type, status, amount=0, path="", extra=""):
    logger.info(
        "",
        extra={
            "event_type": event_type,
            "status": status,
            "amount": amount,
            "path": path,
            "extra": extra
        }
    )

# --------------------------
# Flask routes
# --------------------------
@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)

@app.route("/add/<int:product_id>")
def add_to_cart(product_id):
    quantity = int(request.args.get("quantity", 1))
    cart = session.get("cart", [])
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    
    if product:
        for _ in range(quantity):
            cart.append(product)
        session["cart"] = cart
        log_event("CART", "ADD", amount=(product["price"] * quantity), path=f"/add/{product_id}")
    
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    total = sum(item["price"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/checkout")
def checkout():
    cart = session.get("cart", [])
    if not cart:
        return redirect(url_for("index"))

    total = sum(item["price"] for item in cart)

    # Simulate payment outcome (70% success rate)
    if random.random() < 0.7:
        result = {"status": "success", "amount": total}
        log_event("PAYMENT", "SUCCESS", amount=total, path="/checkout")
    else:
        result = {"status": "fail", "amount": total, "extra": "Transaction declined"}
        log_event("PAYMENT", "FAILED", amount=total, path="/checkout", extra="Transaction declined")

    # Clear cart after checkout
    session["cart"] = []
    return render_template("result.html", result=result)

@app.route("/monitor")
def monitor():
    return render_template("monitor.html")

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# --------------------------
# Error handlers
# --------------------------
@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", error="Internal server error"), 500

# --------------------------
# Run Flask app
# --------------------------
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
