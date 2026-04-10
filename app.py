from flask import Flask, jsonify
from flask_cors import CORS
import cloudscraper

app = Flask(**name**)
CORS(app)

scraper = cloudscraper.create_scraper()

@app.route(’/hltv/matches’)
def hltv_matches():
try:
r = scraper.get(‘https://www.hltv.org/matches’)
return jsonify({“html”: r.text, “status”: r.status_code})
except Exception as e:
return jsonify({“error”: str(e)}), 500

@app.route(’/hltv/stats/players’)
def hltv_players():
try:
r = scraper.get(‘https://www.hltv.org/stats/players?startDate=2025-01-01&endDate=2025-12-31&rankingFilter=Top30’)
return jsonify({“html”: r.text, “status”: r.status_code})
except Exception as e:
return jsonify({“error”: str(e)}), 500

@app.route(’/vlr/matches’)
def vlr_matches():
try:
r = scraper.get(‘https://www.vlr.gg/matches’)
return jsonify({“html”: r.text, “status”: r.status_code})
except Exception as e:
return jsonify({“error”: str(e)}), 500

@app.route(’/vlr/stats’)
def vlr_stats():
try:
r = scraper.get(‘https://www.vlr.gg/stats’)
return jsonify({“html”: r.text, “status”: r.status_code})
except Exception as e:
return jsonify({“error”: str(e)}), 500

@app.route(’/health’)
def health():
return jsonify({“status”: “ok”})

if **name** == ‘**main**’:
app.run(host=‘0.0.0.0’, port=10000)
