import requests
from bs4 import BeautifulSoup

def searchPlayer(name):
    try:
        url = 'https://renderz.app/api/search/elasticsearch'
        data = {
  "query": {
    "bool": {
      "must": [
        {
          "query_string": {
            "fields": [
              "cardName",
              "commonName",
              "firstName",
              "lastName"
            ],
            "query": ""+name+"*",
          }
        }
      ],
      "should": [],
      "must_not": []
    }
  },
  "sort": [
    {
      "rating": {
        "order": "desc"
      }
    },
    {
      "assetId": {
        "order": "desc"
      }
    }
  ],
  "_source": [],
  "from": 0,
  "size": 40
}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
              # Devuelve la respuesta JSON del servidor
        else:
            return f'Error: {response.status_code}'
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
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # Devuelve el contenido HTML de la página
        else:
            return f'Error: {response.status_code}'
    except Exception as e:
        return f'Error: {e}'
    
def getInfoPlayerBoost(id, data, level=None, skill=None):
    try:
        url = getUrlUpgrade(id)
        rank = data
        level = level if level is not None else 0 # Default to level 30 if not provided
        skill = skill if skill is not None else [] # Default to empty list if not provided
        data = {
            "upgradeModels": {
              "level": level,
              "rankUp": rank,
              
              "skillUpgrades": skill
          },
          "playerId": id
        }
        print(data)
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
              # Devuelve la respuesta JSON del servidor
        else:
            return f'Error: {response.status_code}'
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
              if(i == 3):
                isExpired = True if redeem_data[i+4]['expired'] == 6 else False
              else:
                isExpired = True if redeem_data[i+3]['expired'] == 6 else False

              codes.append({
                  "code": code,
                  "reward": reward,
                  "expired": expired,
                  "isExpired": isExpired
              })
              i += 4
          except IndexError:
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