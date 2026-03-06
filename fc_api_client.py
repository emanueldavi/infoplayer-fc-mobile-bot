"""
FC API client - Retrieves player statistics from api.msmc.cc.
Uses requests and JSON file caching.
"""
import json
import os
from urllib.parse import quote

import requests

CACHE_FILE = "players_cache.json"
API_BASE = "https://api.msmc.cc/api/fc25/player/name"


def _load_cache() -> dict:
    """Load cache from JSON file."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {}


def _save_cache(cache: dict) -> None:
    """Save cache to JSON file."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except IOError:
        pass


def get_player_stats(player_name: str) -> dict:
    """
    Get player statistics from FC API.
    Returns normalized dict or error dict.
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

    url = f"{API_BASE}/{quote(player_name.strip())}"
    try:
        resp = requests.get(url, timeout=15)
    except requests.exceptions.Timeout:
        return {"error": "timeout", "message": "Tiempo de espera agotado."}
    except requests.exceptions.RequestException:
        return {"error": "connection_error", "message": "Error de conexión."}

    if resp.status_code == 404:
        result = {"error": "player_not_found", "message": "Jugador no encontrado."}
        cache[name_key] = result
        _save_cache(cache)
        return result

    if resp.status_code != 200:
        result = {"error": "api_error", "message": "La API no está disponible."}
        cache[name_key] = result
        _save_cache(cache)
        return result

    try:
        data = resp.json()
    except json.JSONDecodeError:
        result = {"error": "invalid_response", "message": "Respuesta inválida de la API."}
        cache[name_key] = result
        _save_cache(cache)
        return result

    if not isinstance(data, dict):
        result = {"error": "invalid_response", "message": "Respuesta inválida de la API."}
        cache[name_key] = result
        _save_cache(cache)
        return result

    name = data.get("Name") or data.get("name") or ""
    if not name:
        result = {"error": "player_not_found", "message": "Jugador no encontrado."}
        cache[name_key] = result
        _save_cache(cache)
        return result

    def _to_str(val):
        return str(val) if val is not None else ""

    result = {
        "name": _to_str(name),
        "ovr": _to_str(data.get("OVR") or data.get("ovr") or ""),
        "position": _to_str(data.get("Position") or data.get("position") or "N/A"),
        "pace": _to_str(data.get("PAC") or data.get("pace") or "0"),
        "shooting": _to_str(data.get("SHO") or data.get("shooting") or "0"),
        "passing": _to_str(data.get("PAS") or data.get("passing") or "0"),
        "dribbling": _to_str(data.get("DRI") or data.get("dribbling") or "0"),
        "defending": _to_str(data.get("DEF") or data.get("defending") or "0"),
        "physical": _to_str(data.get("PHY") or data.get("physical") or "0"),
        "team": _to_str(data.get("Team") or data.get("team") or ""),
    }

    cache[name_key] = result
    _save_cache(cache)
    return result
