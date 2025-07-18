from flask import Flask, jsonify, request, make_response
import time
import psutil

app = Flask(__name__)

# Configs 
START_TIME = time.time()
REQUEST_LOG = []

TARGET_200_URL = "/ok"
TARGET_500_URL = "/fail"
ALLOWED_ORIGIN = "http://localhost:3000"  

#  Performance Test 
@app.route("/test/performance")
def test_performance():
    start = time.time()
    time.sleep(0.2)  
    content = "Hello world!" * 1000  
    end = time.time()
    
    response_time = (end - start) * 1000  
    response_size_kb = len(content.encode()) / 1024
    
    return jsonify({
        "status": "pass",
        "response_time_ms": round(response_time, 2),
        "response_size_kb": round(response_size_kb, 2)
    })

#  CPU + RAM Test 
@app.route("/test/resources")
def test_resources():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    return jsonify({
        "cpu_usage_percent": cpu,
        "ram_usage_percent": ram
    })

# Test (Requests Per Minute) 
@app.route("/test/load")
def test_load():
    current_time = time.time()
    global REQUEST_LOG
    REQUEST_LOG = [t for t in REQUEST_LOG if current_time - t < 60]
    REQUEST_LOG.append(current_time)
    return jsonify({
        "requests_last_60_seconds": len(REQUEST_LOG)
    })

#  Endpoint with 200 
@app.route(TARGET_200_URL)
def return_ok():
    return jsonify({"message": "This is a 200 OK response"}), 200

#  Endpoint with 500 
@app.route(TARGET_500_URL)
def return_fail():
    return jsonify({"error": "This is a simulated server error"}), 500

#  Allowed CORS Test 
@app.route("/test/cors-allowed")
def cors_allowed():
    origin = request.headers.get("Origin", "")
    if origin == ALLOWED_ORIGIN:
        response = jsonify({"status": "pass", "message": "CORS allowed"})
        response.headers["Access-Control-Allow-Origin"] = origin
        return response
    return jsonify({"status": "fail", "message": "Origin not allowed"}), 403

#  Disallowed CORS Test 
@app.route("/test/cors-blocked")
def cors_blocked():
    origin = request.headers.get("Origin", "")
    if origin == ALLOWED_ORIGIN:
        response = jsonify({"status": "pass", "message": "CORS allowed"})
        response.headers["Access-Control-Allow-Origin"] = origin
        return response
    return jsonify({"status": "fail", "message": "Origin not allowed"}), 403

#  Health Check
@app.route("/")
def index():
    return " Server is running", 200

# Run App 
if __name__ == "__main__":
    app.run(debug=True)
