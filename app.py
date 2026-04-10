from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

PANDASCORE_TOKEN = "5Hxjg4mKCgSFUSudQgPhCz3srNh4v44drWouXsWJ958SHmlNUo8"
HEADERS = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}

@app.route('/panda/<game>/<path:rest>')
def pandascore_proxy(game, rest):
    try:
        url = f"https://api.pandascore.co/{game}/{rest}"
        r = requests.get(url, headers=HEADERS, params=dict(request.args), timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    return jsonify({"status": "ok", "message": "backend working"})

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
