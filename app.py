import os
import time
import psutil
import requests
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

# Load test URL
TARGET_URL = os.getenv("TARGET_URL", "https://jsonplaceholder.typicode.com/posts")
DISALLOWED_CORS_URL = os.getenv("DISALLOWED_CORS_URL", "https://www.google.com")


@app.route("/")
def home():
    return " Server is Running!"


# Performance Test - Response time and size
@app.route("/test/performance")
def test_performance():
    try:
        start = time.time()
        response = requests.get(TARGET_URL)
        duration_ms = round((time.time() - start) * 1000, 2)
        size_kb = round(len(response.content) / 1024, 2)

        return jsonify({
            "url": TARGET_URL,
            "status_code": response.status_code,
            "response_time_ms": duration_ms,
            "response_size_kb": size_kb
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Resource Test - CPU and RAM
@app.route("/test/resources")
def test_resources():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent

    return jsonify({
        "cpu_usage_percent": cpu,
        "ram_usage_percent": ram
    })


#  Load Test - Request per minute
@app.route("/test/load")
def test_load():
    end_time = time.time() + 10  
    count = 0
    while time.time() < end_time:
        try:
            requests.get(TARGET_URL, timeout=2)
            count += 1
        except:
            count += 1
        time.sleep(0.5)

    rpm = int((count / 10) * 60)
    return jsonify({"requests_per_minute": rpm})


#  Server Error Detection
@app.route("/test/server-error")
def test_server_error():
    test_url = request.args.get("url", TARGET_URL)
    try:
        res = requests.get(test_url)
        if res.status_code >= 500:
            return jsonify({"status": " Server Error", "code": res.status_code}), 500
        return jsonify({"status": " OK", "code": res.status_code})
    except Exception as e:
        return jsonify({"status": " Failed", "error": str(e)}), 500


# CORS Test
@app.route("/test/cors")
def test_cors():
    test_url = request.args.get("url", TARGET_URL)
    try:
        res = requests.options(test_url, headers={
            "Origin": "http://localhost",
            "Access-Control-Request-Method": "GET"
        }, timeout=5)

        cors_header = res.headers.get("Access-Control-Allow-Origin")
        if cors_header == "*" or cors_header == "http://localhost":
            return jsonify({"status": " CORS Allowed", "allowed_origin": cors_header})
        else:
            return jsonify({"status": " CORS Denied", "allowed_origin": cors_header or "None"}), 403

    except Exception as e:
        return jsonify({"status": " Failed", "error": str(e)}), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
