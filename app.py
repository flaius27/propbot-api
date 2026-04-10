from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

PANDASCORE_TOKEN = "5Hxjg4mKCgSFUSudQgPhCz3srNh4v44drWouXsWJ958SHmlNUo8"
HEADERS = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}

@app.route("/")
def index():
    return jsonify({"status": "ok", "routes": ["/proxy", "/test", "/health"]})

@app.route("/proxy")
def proxy_pandascore():
    endpoint = request.args.get("endpoint", "")
    if not endpoint:
        return jsonify({"error": "No endpoint provided"}), 400
    try:
        params = {k: v for k, v in request.args.items() if k != "endpoint"}
        url = f"https://api.pandascore.co/{endpoint}"
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/test")
def test():
    return jsonify({"status": "ok", "message": "backend working v2"})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
