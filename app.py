from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
import os

import os

app = Flask(__name__)
CORS(app)

PANDASCORE_TOKEN = "5Hxjg4mKCgSFUSudQgPhCz3srNh4v44drWouXsWJ958SHmlNUo8"
PANDASCORE_HEADERS = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")

@app.route("/proxy")
def proxy_pandascore():
    endpoint = request.args.get("endpoint", "")
    if not endpoint:
        return jsonify({"error": "No endpoint provided"}), 400
    try:
        params = {k: v for k, v in request.args.items() if k != "endpoint"}
        url = f"https://api.pandascore.co/{endpoint}"
        r = requests.get(url, headers=PANDASCORE_HEADERS, params=params, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hltv/matches")
def hltv_matches():
    try:
        # Trigger Apify HLTV actor
        run_res = requests.post(
            f"https://api.apify.com/v2/acts/J40GPeE23znOF83ep/runs?token={APIFY_TOKEN}",
            json={"matchType": "all", "maxMatches": 20, "includeDetails": True, "minStars": 0},
            timeout=15
        )
        run_data = run_res.json()
        run_id = run_data.get("data", {}).get("id")
        dataset_id = run_data.get("data", {}).get("defaultDatasetId")
        if not run_id:
            return jsonify({"error": "Failed to start Apify run"}), 500

        # Poll until finished (max 60s)
        for _ in range(20):
            time.sleep(3)
            poll = requests.get(
                f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}",
                timeout=10
            )
            status = poll.json().get("data", {}).get("status")
            if status == "SUCCEEDED":
                break
            if status in ["FAILED", "ABORTED"]:
                return jsonify({"error": f"Apify run {status}"}), 500

        items_res = requests.get(
            f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}",
            timeout=10
        )
        return jsonify(items_res.json()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hltv/player")
def hltv_player():
    try:
        player = request.args.get("name", "")
        if not player:
            return jsonify({"error": "No player name provided"}), 400

        # Search HLTV player stats via Apify
        run_res = requests.post(
            f"https://api.apify.com/v2/acts/apify~web-scraper/runs?token={APIFY_TOKEN}",
            json={
                "startUrls": [{"url": f"https://www.hltv.org/stats/players?startDate=2025-01-01&endDate=2026-12-31&rankingFilter=Top30"}],
                "pageFunction": """async function pageFunction(context) {
                    const { $ } = context;
                    const players = [];
                    $('table tbody tr').each((i, row) => {
                        const cols = $(row).find('td');
                        players.push({
                            name: $(cols[0]).text().trim(),
                            team: $(cols[1]).text().trim(),
                            rating: $(cols[2]).text().trim(),
                            kpr: $(cols[3]).text().trim(),
                            adr: $(cols[4]).text().trim(),
                        });
                    });
                    return players;
                }""",
                "maxPagesPerCrawl": 1,
            },
            timeout=15
        )
        run_data = run_res.json()
        run_id = run_data.get("data", {}).get("id")
        dataset_id = run_data.get("data", {}).get("defaultDatasetId")

        import time
        for _ in range(20):
            time.sleep(3)
            poll = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}", timeout=10)
            status = poll.json().get("data", {}).get("status")
            if status == "SUCCEEDED":
                break

        items_res = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}", timeout=10)
        return jsonify(items_res.json()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/test")
def test():
    return jsonify({"status": "ok", "message": "backend working v2"})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/")
def index():
    return jsonify({"status": "ok", "routes": ["/proxy", "/hltv/matches", "/hltv/player", "/test", "/health"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
