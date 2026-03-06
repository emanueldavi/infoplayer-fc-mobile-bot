import requests
from bs4 import BeautifulSoup

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

_RENDERZ_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://renderz.app",
    "Referer": "https://renderz.app/24/players",
}


def _get_renderz_session():
    """Sesión HTTP que evita bloqueos (curl_cffi > cloudscraper > requests)."""
    if HAS_CURL_CFFI:
        s = CurlSession(impersonate="chrome110")
        s.headers.update(_RENDERZ_HEADERS)
        return s
    if HAS_CLOUDSCRAPER:
        s = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        s.headers.update(_RENDERZ_HEADERS)
        return s
    s = requests.Session()
    s.headers.update({
        **_RENDERZ_HEADERS,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    })
    return s


def getStringSkills(id, url):
    cookies = {'locale': 'es-ES'}  # Cambia 'language' por el nombre real de la cookie si es diferente
    respuesta = requests.get(f'https://renderz.app/24/player/{id}', cookies=cookies)
    respuesta.encoding = 'utf-8'  # Asegura que la respuesta se decodifique correctamente
    soup = BeautifulSoup(respuesta.text, 'html.parser')
    img = soup.find('img', {'src': url})
    if img:
        return img.get('alt', None)
    return None


def getSkillsName(idPlayer, skills,):
    SKILLS = {}
    for url in skills:
        id = url.get('id', 'N/A')
        image = url.get('image', 'N/A')
        alt = getStringSkills(idPlayer, image)
        SKILLS[str(id)] = str(alt) if alt is not None else 'N/A'
    return SKILLS


def searchPlayer(name):
    """Busca jugadores en la API de Renderz. Retorna lista de jugadores o string con error."""
    try:
        session = _get_renderz_session()
        # Visitar página primero para cookies
        session.get("https://renderz.app/24/players", timeout=15)
        url = 'https://renderz.app/api/search/elasticsearch'
        data = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "fields": ["cardName", "commonName", "firstName", "lastName"],
                                "query": f"{name}*",
                            }
                        }
                    ],
                    "should": [],
                    "must_not": []
                }
            },
            "sort": [
                {"rating": {"order": "desc"}},
                {"assetId": {"order": "desc"}}
            ],
            "from": 0,
            "size": 40
        }
        response = session.post(url, json=data, timeout=15)
        if response.status_code != 200:
            return f'Error: {response.status_code}'

        result = response.json()

        # Formato 1: API devuelve {"players": [...]}
        if isinstance(result, dict) and 'players' in result:
            return result['players']

        # Formato 2: Elasticsearch estándar {"hits": {"hits": [{"_source": {...}}, ...]}}
        hits = result.get('hits', {}).get('hits', [])
        if hits:
            players = []
            for hit in hits:
                doc = hit.get('_source', hit)
                if isinstance(doc, dict) and (doc.get('assetId') or doc.get('commonName') or doc.get('playerId')):
                    players.append(doc)
            return players if players else None

        return None
    except requests.exceptions.Timeout:
        return 'Error: Timeout'
    except requests.exceptions.RequestException as e:
        return f'Error: {e}'
    except Exception as e:
        return f'Error: {e}'

def getUrlUpgrade(id):
    try:
        return 'https://renderz.app/24/player/'+id+'/upgradePlayer'
    except Exception as e:
        return f'Error: {e}'
    
def getUrlPlayer(id):
    try:
        return 'https://renderz.app/24/player/'+id
    except Exception as e:
        return f'Error: {e}'

def getInfoPlayer(id):
    try:
        url = getUrlPlayer(id)
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # Devuelve el contenido HTML de la página
        else:
            return f'Error: {response.status_code}'
    except Exception as e:
        return f'Error: {e}'
    
def getInfoPlayerBoost(id, data, level=None, skill=None):
    try:
        session = _get_renderz_session()
        session.get("https://renderz.app/24/players", timeout=15)
        url = getUrlUpgrade(id)
        rank = data
        level = level if level is not None else 0
        skill = skill if skill is not None else []
        payload = {
            "upgradeModels": {
                "level": level,
                "rankUp": rank,
                "skillUpgrades": skill
            },
            "playerId": id
        }
        response = session.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()
        return f'Error: {response.status_code}'
    except requests.exceptions.Timeout:
        return 'Error: Timeout'
    except requests.exceptions.RequestException as e:
        return f'Error: {e}'
    except Exception as e:
        return f'Error: {e}'
    

def getRedeemCodes():
  url = "https://renderz.app/redeem-codes/__data.json"
  headers = {
      "User-Agent": "Mozilla/5.0"
  }

  response = requests.get(url, headers=headers)
  data = response.json()

  redeem_data = data["nodes"][2]["data"]

  codes = []
  i = 0
  while i < len(redeem_data):
      # Solo procesa si es un string en mayúsculas (código)
      if isinstance(redeem_data[i], str) and redeem_data[i].isupper() and len(redeem_data[i]) >= 5:
          try:
              code = redeem_data[i]
              reward = redeem_data[i+1]
              expired = redeem_data[i+2]
              # Buscar el objeto con 'expired' en los siguientes elementos
              isExpired = False
              for j in range(i+3, min(i+5, len(redeem_data))):
                  if isinstance(redeem_data[j], dict) and 'expired' in redeem_data[j]:
                      isExpired = redeem_data[j]['expired'] == 6
                      break

              codes.append({
                  "code": code,
                  "reward": reward,
                  "expired": expired,
                  "isExpired": isExpired
              })
              i += 4
          except (IndexError, KeyError, TypeError):
              break
      else:
          i += 1
  return codes


# Ejemplo de uso
    # try:
    #     respuesta = requests.get(url)
    #     if respuesta.status_code == 200:
    #         soup = BeautifulSoup(respuesta.text, 'html.parser')
    #         titulo = soup.title.string if soup.title else 'Sin título'
    #         return titulo
    #     else:
    #         return f'Error al acceder a la página: {respuesta.status_code}'
    # except Exception as e:
    #     return f'Error: {e}'