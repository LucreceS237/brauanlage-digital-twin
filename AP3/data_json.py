import requests

url = "http://192.168.0.100:5000/api/status"
response = requests.get(url, timeout=2)

data = response.json()
print(data)