import requests

url = "https://unipass.customs.go.kr:38010/ext/rest/cargCsclPrgsInfoQry/retrieveCargCsclPrgsInfo?crkyCn=i230k186p083p151k070n090z2&cargMtNo=24YPZ40102I00020001"

payload = {}
headers = {
  'Cookie': 'WMONID=Vhc91qpwkUo'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)