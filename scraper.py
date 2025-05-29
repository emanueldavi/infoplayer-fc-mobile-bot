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
    
def getInfoPlayerBoost(id, data):
    try:
        url = getUrlUpgrade(id)
        rank = data
        data = {
            "upgradeModels": {
              # "level": 30,
              "rankUp": rank[4:],
              "skillUpgrades": [
              {
                "id": 9020,
                "level": 3
              }
            ]
          },
          "playerId": id
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
              # Devuelve la respuesta JSON del servidor
        else:
            return f'Error: {response.status_code}'
    except Exception as e:
      return f'Error: {e}'


# Ejemplo de uso
# print(fetch_url('https://www.example.com'))
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