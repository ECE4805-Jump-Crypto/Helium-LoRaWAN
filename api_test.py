import json
import requests

lat = 44.79406735325452
lon = -106.95872819992391
dist = 5500 #distance in meters
url = "https://api.helium.io/v1/hotspots/location/distance?lat={}&lon={}&distance={}".format(lat,lon,dist)

#defauilt payload and headers
payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(json.dumps(response.json(), indent=4))