from flask import Flask

import folium
import json
import requests


"""
The following block of code pulls the nearby node data at the given distance from the given latitude and 
longitude. The distance should be kept at 12000 meters but the latitude and longitude can be adjusted for
the proposed node location.
"""
lat = 44.79806735325452
lon = -106.95872819992391
dist = 12000 #distance in meters
url = "https://api.helium.io/v1/hotspots/location/distance?lat={}&lon={}&distance={}".format(lat,lon,dist)

#defauilt payload and headers
payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)
data = response.json()
num_nodes = len(data["data"])

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
    folium.Circle([lat,lon], radius=12000, color='yellow').add_to(folium_map)
    #urban circle bound
    folium.Circle([lat,lon], radius=5000, color='green').add_to(folium_map)

    #user input location
    folium.CircleMarker([lat,lon],
                    radius=5,
                    color='blue',
                    fill_color='blue').add_to(folium_map)

    #nearby node markers
    for i in range(0,num_nodes-1):
        if data["data"][i]["status"]["online"] == "online":
            status_color = 'green'  # green marker indicates online node
        else:
            status_color = 'red'    # red marker indicates offline node

        folium.CircleMarker([data["data"][i]["lat"],data["data"][i]["lng"]],
                        radius=5,
                        color=status_color,
                        fill_color=status_color,
                        popup=data["data"][i]["name"]).add_to(folium_map)

    return folium_map._repr_html_()


if __name__ == '__main__':
    app.run(debug=True)