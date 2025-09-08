from flask import Flask, render_template, jsonify
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
import pandas as pd
import threading
import time
import os
import logging
from datetime import datetime

# Flask app setup
app = Flask(__name__)

# Configuration
LOG_FILE = "logs/payments.log"
ANOMALY_THRESHOLD = 0.1
MIN_LOGS_FOR_TRAINING = 20

# Global variables
processed_logs = []
anomaly_results = []
df_all = pd.DataFrame()
model = IsolationForest(contamination=ANOMALY_THRESHOLD, random_state=42)
svm_model = OneClassSVM(gamma='scale', nu=ANOMALY_THRESHOLD)
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
model_fitted = False
svm_fitted = False
rf_fitted = False
monitoring_active = True

# Set up logging for the AI monitor
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_log_line(line):
    """Parse structured log line into dictionary"""
    try:
        parts = line.strip().split(" | ")
        if len(parts) >= 5:
            return {
                "timestamp": parts[0],
                "type": parts[2],
                "status": parts[3],
                "amount": float(parts[4]) if parts[4] != '0' else 0,
                "path": parts[5] if len(parts) > 5 else "",
                "extra": parts[6] if len(parts) > 6 else ""
            }
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to parse log line: {line.strip()}")
        return None

def classify_anomaly(log):
    """Apply business rules for anomaly detection"""
    amount = log.get("amount", 0)
    
    # Rule-based anomaly detection
    if amount >= 10000:
        return "Anomaly"
    elif amount < 200 and log.get("type") == "PAYMENT":
        return "Anomaly"
    elif "fraud" in log.get("extra", "").lower():
        return "Anomaly"
    elif "injection" in log.get("extra", "").lower():
        return "Anomaly"
    elif "unauthorized" in log.get("extra", "").lower():
        return "Anomaly"
    
    return None

def monitor_logs():
    """Main log monitoring function"""
    global processed_logs, df_all, model, model_fitted, monitoring_active
    
    # Ensure log file exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
    
    logger.info("Starting log monitoring...")
    
    with open(LOG_FILE, "r") as f:
        # Go to end of file to monitor new entries
        f.seek(0, 2)
        
        while monitoring_active:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            log = parse_log_line(line)
            if not log:
                continue

            # Apply rule-based anomaly detection first
            rule_based_anomaly = classify_anomaly(log)
            if rule_based_anomaly:
                log["anomaly"] = rule_based_anomaly
                processed_logs.append(log)
                logger.info(f"Rule-based anomaly detected: {log}")
                continue

            # Add to training data
            df_all = pd.concat([df_all, pd.DataFrame([log])], ignore_index=True)
            
            # Train model after collecting enough data
            if not model_fitted and len(df_all) >= MIN_LOGS_FOR_TRAINING:
                try:
                    # Prepare features for training
                    df_features = prepare_features(df_all)
                    model.fit(df_features)
                    model_fitted = True
                    logger.info(f"Isolation Forest trained with {len(df_all)} samples")
                    
                    # Train SVM model
                    svm_model.fit(df_features)
                    svm_fitted = True
                    logger.info(f"SVM model trained with {len(df_all)} samples")
                    
                except Exception as e:
                    logger.error(f"Model training failed: {e}")
            
            # Predict anomaly using ML model
            if model_fitted:
                try:
                    df_new = prepare_features(pd.DataFrame([log]))
                    prediction = model.predict(df_new)[0]
                    isolation_result = "Normal" if prediction == 1 else "Anomaly"
                    
                    # SVM prediction
                    svm_result = "Normal"
                    if svm_fitted:
                        svm_prediction = svm_model.predict(df_new)[0]
                        svm_result = "Normal" if svm_prediction == 1 else "Anomaly"
                    
                    # Combine results for final decision
                    if isolation_result == "Anomaly" or svm_result == "Anomaly":
                        log["anomaly"] = "Anomaly"
                    else:
                        log["anomaly"] = "Normal"
                    
                    # Store detailed results
                    anomaly_detail = {
                        "timestamp": log["timestamp"],
                        "type": log["type"],
                        "status": log["status"],
                        "amount": log["amount"],
                        "isolation_forest": isolation_result,
                        "svm": svm_result,
                        "final_decision": log["anomaly"],
                        "confidence": "High" if isolation_result == svm_result else "Medium",
                        "extra": log.get("extra", "")
                    }
                    anomaly_results.append(anomaly_detail)
                    
                except Exception as e:
                    logger.error(f"Prediction failed: {e}")
                    log["anomaly"] = "Error"
            else:
                log["anomaly"] = "Training"

            processed_logs.append(log)
            
            # Keep only recent logs in memory (last 1000)
            if len(processed_logs) > 1000:
                processed_logs = processed_logs[-1000:]
            
            # Keep only recent anomaly results (last 500)
            if len(anomaly_results) > 500:
                anomaly_results = anomaly_results[-500:]

def prepare_features(df):
    """Prepare features for machine learning model"""
    df_features = pd.get_dummies(df[["type", "status"]], prefix_sep="_")
    df_features["amount"] = df["amount"]
    
    # Ensure consistent columns
    expected_columns = [
        'type_CART', 'type_PAYMENT', 'type_SECURITY',
        'status_ADD', 'status_SUCCESS', 'status_FAILED',
        'amount'
    ]
    
    for col in expected_columns:
        if col not in df_features.columns:
            df_features[col] = 0
    
    return df_features[expected_columns]

# Flask routes
@app.route("/")
def index():
    """Main monitoring dashboard"""
    recent_logs = processed_logs[-50:] if processed_logs else []
    return render_template("monitor.html", logs=recent_logs)

@app.route("/logs")
def get_logs():
    """API endpoint for real-time log updates"""
    recent_logs = processed_logs[-50:] if processed_logs else []
    return jsonify(recent_logs)

@app.route("/anomalies")
def get_anomalies():
    """API endpoint for anomaly analysis results"""
    recent_anomalies = anomaly_results[-100:] if anomaly_results else []
    return jsonify(recent_anomalies)
@app.route("/stats")
def get_stats():
    """API endpoint for monitoring statistics"""
    if not processed_logs:
        return jsonify({"total": 0, "anomalies": 0, "normal": 0})
    
    total = len(processed_logs)
    anomalies = len([log for log in processed_logs if log.get("anomaly") == "Anomaly"])
    normal = len([log for log in processed_logs if log.get("anomaly") == "Normal"])
    
    return jsonify({
        "total": total,
        "anomalies": anomalies,
        "normal": normal,
        "model_fitted": model_fitted,
        "svm_fitted": svm_fitted,
        "anomaly_rate": round((anomalies / total) * 100, 2) if total > 0 else 0
    })


@app.route("/cart")
def cart():
    return render_template("cart.html")  # Uses the same cart.html as app.py

@app.route("/monitor")
def monitor():
    return render_template("monitor.html")  # Same as app.py




@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "monitoring_active": monitoring_active,
        "model_fitted": model_fitted,
        "logs_processed": len(processed_logs),
        "timestamp": datetime.now().isoformat()
    })

def shutdown_monitor():
    """Gracefully shutdown the monitor"""
    global monitoring_active
    monitoring_active = False
    logger.info("Log monitor shutting down...")

# Start monitoring thread
monitor_thread = threading.Thread(target=monitor_logs, daemon=True)
monitor_thread.start()

if __name__ == "__main__":
    try:
        port = int(os.environ.get('AI_MONITOR_PORT', 9000))
        app.run(host="0.0.0.0", port=port, debug=False)
    except KeyboardInterrupt:
        shutdown_monitor()
