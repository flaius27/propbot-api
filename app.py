from flask import Flask, jsonify
from flask_cors import CORS
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

def parse_hltv_matches(html):
    soup = BeautifulSoup(html, 'html5lib')
    matches = []
    for match in soup.select('.upcomingMatch')[:10]:
        try:
            teams = match.select('.matchTeamName')
            event = match.select_one('.matchEventName')
            time = match.select_one('.matchTime')
            matches.append({
                'team1': teams[0].text.strip() if len(teams) > 0 else 'TBD',
                'team2': teams[1].text.strip() if len(teams) > 1 else 'TBD',
                'event': event.text.strip() if event else '',
                'time': time.text.strip() if time else '',
            })
        except:
            continue
    return matches

def parse_hltv_players(html):
    soup = BeautifulSoup(html, 'html.parser')
    players = []
    for row in soup.select('table tbody tr')[:20]:
        try:
            cols = row.select('td')
            if len(cols) >= 5:
                players.append({
                    'name': cols[0].text.strip(),
                    'team': cols[1].text.strip(),
                    'rating': cols[2].text.strip(),
                    'kpr': cols[3].text.strip(),
                    'adr': cols[4].text.strip() if len(cols) > 4 else '',
                })
        except:
            continue
    return players

def parse_vlr_matches(html):
    soup = BeautifulSoup(html, 'html.parser')
    matches = []
    for match in soup.select('.match-item')[:10]:
        try:
            teams = match.select('.match-item-vs-team-name')
            event = match.select_one('.match-item-event')
            matches.append({
                'team1': teams[0].text.strip() if len(teams) > 0 else 'TBD',
                'team2': teams[1].text.strip() if len(teams) > 1 else 'TBD',
                'event': event.text.strip() if event else '',
            })
        except:
            continue
    return matches

def parse_vlr_stats(html):
    soup = BeautifulSoup(html, 'html.parser')
    players = []
    for row in soup.select('table tbody tr')[:20]:
        try:
            cols = row.select('td')
            if len(cols) >= 4:
                players.append({
                    'name': cols[0].text.strip(),
                    'team': cols[1].text.strip(),
                    'acs': cols[2].text.strip(),
                    'kd': cols[3].text.strip(),
                })
        except:
            continue
    return players

@app.route('/hltv/matches')
def hltv_matches():
    try:
        r = scraper.get('https://www.hltv.org/matches', timeout=10)
        matches = parse_hltv_matches(r.text)
        return jsonify({'matches': matches, 'status': r.status_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hltv/stats/players')
def hltv_players():
    try:
        r = scraper.get('https://www.hltv.org/stats/players?startDate=2025-01-01&endDate=2025-12-31&rankingFilter=Top30', timeout=10)
        players = parse_hltv_players(r.text)
        return jsonify({'players': players, 'status': r.status_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vlr/matches')
def vlr_matches():
    try:
        r = scraper.get('https://www.vlr.gg/matches', timeout=10)
        matches = parse_vlr_matches(r.text)
        return jsonify({'matches': matches, 'status': r.status_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vlr/stats')
def vlr_stats():
    try:
        r = scraper.get('https://www.vlr.gg/stats', timeout=10)
        players = parse_vlr_stats(r.text)
        return jsonify({'players': players, 'status': r.status_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
