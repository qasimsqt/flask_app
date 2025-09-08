import random
import logging
import time
import os
import signal
import sys
from datetime import datetime

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure structured logging to payments.log
logging.basicConfig(
    filename="logs/payments.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(type)s | %(status)s | %(amount)s | %(path)s | %(extra)s"
)
logger = logging.getLogger("log_generator")

# Helper function for structured logs
def log_event(event_type, status, amount=0, path="", extra=""):
    logger.info("", extra={
        "type": event_type,
        "status": status,
        "amount": amount,
        "path": path,
        "extra": extra
    })

# Normal payment events
def normal_checkout():
    if random.random() < 0.7:
        amount = random.randint(50, 1000)
        log_event("PAYMENT", "SUCCESS", amount=amount, path="/checkout")
    else:
        amount = random.randint(50, 1000)
        log_event("PAYMENT", "FAILED", amount=amount, path="/checkout", extra="Transaction declined")

def normal_cart_activity():
    """Generate normal cart activities"""
    product_ids = list(range(1, 12))
    product_id = random.choice(product_ids)
    amount = random.randint(200, 1000)
    log_event("CART", "ADD", amount=amount, path=f"/add/{product_id}")

# Malicious/Anomaly events
def malicious_event():
    events = [
        lambda: log_event("SECURITY", "FAILED", amount=0, path="/login", extra="FAILED LOGIN attempt user=admin"),
        lambda: log_event("PAYMENT", "FAILED", amount=99999, path="/checkout", extra="Possible fraud detected - unusually high amount"),
        lambda: log_event("SECURITY", "FAILED", amount=0, path="/admin", extra="Unauthorized access attempt"),
        lambda: log_event("SECURITY", "FAILED", amount=0, path="/search", extra="SQL Injection attempt id=' OR '1'='1"),
        lambda: log_event("PAYMENT", "SUCCESS", amount=15000, path="/checkout", extra="Suspicious high-value transaction"),
        lambda: log_event("CART", "ADD", amount=50, path="/add/1", extra="Unusually low amount - possible testing"),
    ]
    random.choice(events)()

def generate_logs():
    """Main log generation loop"""
    print(f"[{datetime.now()}] Starting log generator... Press Ctrl+C to stop")
    
    try:
        while True:
            # 70% normal activity, 20% cart activity, 10% anomalies
            rand = random.random()
            if rand < 0.7:
                normal_checkout()
            elif rand < 0.9:
                normal_cart_activity()
            else:
                malicious_event()
            
            # Random sleep between 0.5 and 3 seconds
            time.sleep(random.uniform(0.5, 3.0))
            
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Log generator stopped by user. Goodbye!")
        sys.exit(0)

def signal_handler(signum, frame):
    """Handle termination signals gracefully"""
    print(f"\n[{datetime.now()}] Received signal {signum}. Shutting down log generator...")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    generate_logs()
