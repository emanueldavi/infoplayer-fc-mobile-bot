"""
RenderZ client - Scrapes player statistics from RenderZ website.
Uses requests, BeautifulSoup, and JSON file caching.
"""
import json
import os
import re
import requests
from bs4 import BeautifulSoup

try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False

CACHE_FILE = "players_cache.json"
BASE_URL = "https://renderz.app"
PLAYERS_URL = f"{BASE_URL}/24/players"
PLAYER_PAGE_URL = f"{BASE_URL}/24/player"
SEARCH_API_URL = f"{BASE_URL}/api/search/elasticsearch"


def _get_session():
    """Create a session (cloudscraper or requests) for bypassing bot protection."""
    if HAS_CLOUDSCRAPER:
        session = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
    else:
        session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": BASE_URL,
        "Referer": f"{PLAYERS_URL}",
    })
    return session


def _load_cache():
    """Load cache from JSON file."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {}


def _save_cache(cache):
    """Save cache to JSON file."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except IOError:
        pass


def _search_player_id(player_name: str) -> str | None:
    """Search for player on RenderZ and return assetId of first match."""
    try:
        session = _get_session()
        payload = {
            "query": {
                "bool": {
                    "must": [{
                        "query_string": {
                            "fields": ["cardName", "commonName", "firstName", "lastName"],
                            "query": f"{player_name}*",
                        }
                    }],
                    "should": [],
                    "must_not": []
                }
            },
            "sort": [{"rating": {"order": "desc"}}, {"assetId": {"order": "desc"}}],
            "from": 0,
            "size": 5
        }
        resp = session.post(SEARCH_API_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if resp.status_code != 200:
            return None
        data = resp.json()
        hits = data.get('hits', {}).get('hits', [])
        if not hits:
            players = data.get('players', [])
            if players:
                p = players[0]
                return str(p.get('assetId') or p.get('playerId') or '')
            return None
        doc = hits[0].get('_source', hits[0])
        return str(doc.get('assetId') or doc.get('playerId') or '')
    except Exception:
        return None


def _scrape_player_page(asset_id: str) -> dict | None:
    """Scrape player statistics from RenderZ player page HTML."""
    url = f"{PLAYER_PAGE_URL}/{asset_id}"
    try:
        session = _get_session()
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            return None
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        data = {"url": url}
        name_el = soup.find('h1') or soup.find(class_=re.compile(r'name|title|player', re.I))
        if name_el:
            data["name"] = name_el.get_text(strip=True)
        else:
            title = soup.find('title')
            if title:
                data["name"] = title.get_text(strip=True).split('|')[0].strip()
            else:
                data["name"] = "Unknown"
        text = soup.get_text()
        ovr_match = re.search(r'(\d{2,3})\s*\n\s*[A-Z]{2}\b', text)
        if ovr_match:
            data["ovr"] = int(ovr_match.group(1))
        else:
            ovr_alt = re.search(r'OVR[:\s]*(\d{2,3})', text, re.I)
            data["ovr"] = int(ovr_alt.group(1)) if ovr_alt else 0
        pos_match = re.search(r'\b([A-Z]{2,4})\b', text)
        data["position"] = pos_match.group(1) if pos_match else "N/A"
        stats_map = [
            ("pace", r"Pace\s*(\d{2,3})"),
            ("shooting", r"Shooting\s*(\d{2,3})"),
            ("passing", r"Passing\s*(\d{2,3})"),
            ("dribbling", r"Dribbling\s*(\d{2,3})"),
            ("defending", r"Defending\s*(\d{2,3})"),
            ("physical", r"Physical\s*(\d{2,3})"),
        ]
        for key, pattern in stats_map:
            m = re.search(pattern, text)
            data[key] = int(m.group(1)) if m else 0
        if data.get("name") and (data.get("ovr") or any(data.get(k) for k, _ in stats_map)):
            return data
        return None
    except Exception:
        return None


def _scrape_from_data_json(asset_id: str) -> dict | None:
    """Try to get player data from __data.json (SvelteKit endpoint)."""
    url = f"{PLAYER_PAGE_URL}/{asset_id}/__data.json"
    try:
        session = _get_session()
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            return None
        text = resp.text
        name_match = re.search(r'"commonName":"([^"]+)"', text)
        name = name_match.group(1) if name_match else None
        if not name:
            name_match = re.search(r'"cardName":"([^"]+)"', text)
            name = name_match.group(1) if name_match else "Unknown"
        ovr_match = re.search(r'"rating":(\d+)', text)
        ovr = int(ovr_match.group(1)) if ovr_match else 0
        pos_match = re.search(r'"position":"([A-Z]{2,4})"', text)
        pos = pos_match.group(1) if pos_match else "N/A"
        avg_match = re.search(
            r'"avg1":\d+,"avg2":\d+,"avg3":\d+,"avg4":\d+,"avg5":\d+,"avg6":\d+\},(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)',
            text
        )
        if avg_match:
            pace, shooting, passing, dribbling, defending, physical = (int(x) for x in avg_match.groups())
        else:
            pace = shooting = passing = dribbling = defending = physical = 0
        return {
            "name": name or "Unknown",
            "ovr": ovr,
            "position": pos,
            "pace": pace,
            "shooting": shooting,
            "passing": passing,
            "dribbling": dribbling,
            "defending": defending,
            "physical": physical,
            "url": f"{PLAYER_PAGE_URL}/{asset_id}",
        }
    except Exception:
        return None


def get_player_stats(player_name: str) -> dict:
    """
    Get player statistics from RenderZ.
    Returns structured data or raises/returns error dict.
    Uses local JSON cache.
    """
    if not player_name or not str(player_name).strip():
        return {"error": "player_not_found", "message": "Nombre de jugador vacío."}
    name_key = str(player_name).strip().lower()
    cache = _load_cache()
    if name_key in cache:
        cached = cache[name_key]
        if isinstance(cached, dict) and "error" not in cached:
            return cached
        if isinstance(cached, dict) and cached.get("error") == "player_not_found":
            return cached
    asset_id = _search_player_id(player_name)
    if not asset_id:
        result = {"error": "player_not_found", "message": "Jugador no encontrado."}
        cache[name_key] = result
        _save_cache(cache)
        return result
    data = _scrape_from_data_json(asset_id)
    if not data:
        data = _scrape_player_page(asset_id)
    if not data:
        result = {"error": "scrape_failed", "message": "No se pudieron obtener las estadísticas."}
        cache[name_key] = result
        _save_cache(cache)
        return result
    result = {
        "name": data.get("name", "Unknown"),
        "ovr": data.get("ovr", 0),
        "position": data.get("position", "N/A"),
        "pace": data.get("pace", 0),
        "shooting": data.get("shooting", 0),
        "passing": data.get("passing", 0),
        "dribbling": data.get("dribbling", 0),
        "defending": data.get("defending", 0),
        "physical": data.get("physical", 0),
        "url": data.get("url", f"{PLAYER_PAGE_URL}/{asset_id}"),
    }
    cache[name_key] = result
    _save_cache(cache)
    return result
