import requests

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
            codes.append({
                "code": code,
                "reward": reward,
                "expired": expired
            })
            i += 4
        except IndexError:
            break
    else:
        i += 1

# Mostrar todos los códigos y recompensas
for c in codes:
    print(f"{c['code']}: {c['reward']} (Expira: {c['expired']})\n")