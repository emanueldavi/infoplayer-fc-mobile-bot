"""
RenderZ client - Scrapes player statistics from RenderZ website.
Uses curl_cffi, cloudscraper, or requests with BeautifulSoup and JSON caching.
"""
import json
import os
import re
import requests
from bs4 import BeautifulSoup

# Preferencia: curl_cffi (mejor bypass) > cloudscraper > requests
try:
    from curl_cffi.requests import Session as CurlSession
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False

CACHE_FILE = "players_cache.json"
BASE_URL = "https://renderz.app"

# Jugadores populares como último recurso cuando la API falla (403, etc.)
FALLBACK_PLAYERS = {
    "messi": {"name": "Lionel Messi", "ovr": 95, "position": "RW", "pace": 89, "shooting": 94, "passing": 97, "dribbling": 98, "defending": 40, "physical": 75, "url": "https://renderz.app/24/player/158023", "asset_id": "158023"},
    "ronaldo": {"name": "Cristiano Ronaldo", "ovr": 94, "position": "ST", "pace": 90, "shooting": 95, "passing": 82, "dribbling": 89, "defending": 35, "physical": 78, "url": "https://renderz.app/24/player/20801", "asset_id": "20801"},
    "mbappé": {"name": "Kylian Mbappé", "ovr": 96, "position": "ST", "pace": 99, "shooting": 92, "passing": 84, "dribbling": 95, "defending": 38, "physical": 80, "url": "https://renderz.app/24/player/231747", "asset_id": "231747"},
    "mbappe": {"name": "Kylian Mbappé", "ovr": 96, "position": "ST", "pace": 99, "shooting": 92, "passing": 84, "dribbling": 95, "defending": 38, "physical": 80, "url": "https://renderz.app/24/player/231747", "asset_id": "231747"},
    "haaland": {"name": "Erling Haaland", "ovr": 94, "position": "ST", "pace": 89, "shooting": 96, "passing": 72, "dribbling": 82, "defending": 45, "physical": 93, "url": "https://renderz.app/24/player/239085", "asset_id": "239085"},
    "vinicius": {"name": "Vinícius Jr.", "ovr": 93, "position": "LW", "pace": 97, "shooting": 84, "passing": 82, "dribbling": 95, "defending": 35, "physical": 72, "url": "https://renderz.app/24/player/231650", "asset_id": "231650"},
    "bellingham": {"name": "Jude Bellingham", "ovr": 92, "position": "CM", "pace": 84, "shooting": 86, "passing": 88, "dribbling": 90, "defending": 78, "physical": 85, "url": "https://renderz.app/24/player/246173", "asset_id": "246173"},
    "lamine yamal": {"name": "Lamine Yamal", "ovr": 108, "position": "RW", "pace": 127, "shooting": 114, "passing": 111, "dribbling": 127, "defending": 35, "physical": 78, "url": "https://renderz.app/24/player/277643", "asset_id": "277643"},
    "yamal": {"name": "Lamine Yamal", "ovr": 108, "position": "RW", "pace": 127, "shooting": 114, "passing": 111, "dribbling": 127, "defending": 35, "physical": 78, "url": "https://renderz.app/24/player/277643", "asset_id": "277643"},
}
PLAYERS_URL = f"{BASE_URL}/24/players"
PLAYER_PAGE_URL = f"{BASE_URL}/24/player"
SEARCH_API_URL = f"{BASE_URL}/api/search/elasticsearch"

_HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": BASE_URL,
    "Referer": f"{PLAYERS_URL}/",
}


def _get_session():
    """Create session with best available client for bypassing bot protection."""
    if HAS_CURL_CFFI:
        s = CurlSession(impersonate="chrome110")
        s.headers.update(_HEADERS)
        return s
    if HAS_CLOUDSCRAPER:
        s = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        s.headers.update(_HEADERS)
        return s
    s = requests.Session()
    s.headers.update({
        **_HEADERS,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    })
    return s


def _request_get(session, url, **kwargs):
    """GET compatible with curl_cffi and requests."""
    if HAS_CURL_CFFI and isinstance(session, CurlSession):
        return session.get(url, timeout=15, **kwargs)
    return session.get(url, timeout=15, **kwargs)


def _request_post(session, url, json=None, **kwargs):
    """POST compatible with curl_cffi and requests."""
    if HAS_CURL_CFFI and isinstance(session, CurlSession):
        return session.post(url, json=json, timeout=15, **kwargs)
    return session.post(url, json=json, timeout=15, **kwargs)


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
        # Visitar la página primero para obtener cookies (comportamiento tipo navegador)
        _request_get(session, PLAYERS_URL)
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
        resp = _request_post(session, SEARCH_API_URL, json=payload, headers={"Content-Type": "application/json"})
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
        resp = _request_get(session, url)
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
        resp = _request_get(session, url)
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
        # Cuando la API falla (403), usar base local de jugadores populares
        if name_key in FALLBACK_PLAYERS:
            return FALLBACK_PLAYERS[name_key].copy()
        for key, fallback_data in FALLBACK_PLAYERS.items():
            if key in name_key or name_key in key:
                return fallback_data.copy()
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
        "asset_id": asset_id,
    }
    cache[name_key] = result
    _save_cache(cache)
    return result
