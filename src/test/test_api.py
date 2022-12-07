import requests
response = requests.get('https://etl.hotspotty.org/api/v1/hotspots/search/?proximity_hex=8c2ab38000001ff').json()['data']

for hotspot in response:
    if hotspot['online'] == False and hotspot['deny_list'] == True:
        print(hotspot['id'])