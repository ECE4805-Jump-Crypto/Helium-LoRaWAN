from flask import Flask

import folium
import json
import requests
import time


"""
The following block of code pulls the nearby node data at the given distance from the given latitude and 
longitude. The distance should be kept at 12000 meters but the latitude and longitude can be adjusted for
the proposed node location.
"""
lat = 41.881832
lon = -87.623177
dist = 20000 #distance in meters
url = "https://api.helium.io/v1/hotspots/location/distance?lat={}&lon={}&distance={}&page[size]=1000".format(lat,lon,dist)
orig_url = url
#defauilt payload and headers
payload = {}
headers = {}
#List to hold each api request
total_data = []
while url:
    time.sleep(0.1)
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    total_data.append(data)

    url = orig_url #reset url string to have no cursor
    try:
        cursor = data['cursor']
        url += "&cursor={}".format(cursor)
    except:
        url = None


"""
The following block of code establishes a Flask application endpoint for the folium coverage map.

To establish the Flask Aplication run file in the command line:
$ python map_test.py

Flask Apllication Server: http://127.0.0.1:5000/
"""
app = Flask(__name__)
@app.route('/')
def index():
    start_coords = (lat, lon)
    folium_map = folium.Map(location=start_coords, zoom_start=12)

    #rural circle bound
    folium.Circle([lat,lon], radius=20000, color='yellow').add_to(folium_map)
    #urban circle bound
    folium.Circle([lat,lon], radius=5000, color='green').add_to(folium_map)

    #user input location
    folium.CircleMarker([lat,lon],
                    radius=5,
                    color='blue',
                    fill_color='blue').add_to(folium_map)

    #nearby node markers
    for j in range(len(total_data)):
        for i in range(len(total_data[j]["data"])):
            if total_data[j]["data"][i]["status"]["online"] == "online":
                status_color = 'green'  # green marker indicates online node
            else:
                status_color = 'red'    # red marker indicates offline node

            folium.CircleMarker([total_data[j]["data"][i]["lat"],total_data[j]["data"][i]["lng"]],
                            radius=5,
                            color=status_color,
                            fill_color=status_color,
                            popup=total_data[j]["data"][i]["name"]).add_to(folium_map)

    return folium_map._repr_html_()


if __name__ == '__main__':
    app.run(debug=True)