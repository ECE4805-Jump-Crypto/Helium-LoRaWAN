import requests
import numpy
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import time

# Fetch api
url = 'http://localhost:5000/api/v1/hotspots'



# Create api and Post

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

# Create some test data for our catalog in the form of a list of dictionaries.





# @app.route('/', methods=['GET'])
# def home():
#     return Lat


# A route to return all of the available entries in our catalog.
@app.route('/api/v1/prediction', methods=['GET'])
def api_all():
    print('api called')
    r = requests.get(url)
    response = r.json()
    data = numpy.array(response['data'])
    Last = data[-1]
    Lat = numpy.array(Last['Lat'])
    Lng = numpy.array(Last['Lng'])
    elevation = numpy.array(Last['elevation'])
    gain = numpy.array(Last['gain'])
    print('Lat: {}'.format(Lat))
    print('Lng: {}'.format(Lng))
    print('Elevation: {}'.format(elevation))
    print('Gain: {}'.format(gain))
    prediction = [
        {'Prediction': str(gain),
         }
    ]
    print(prediction)
    return jsonify(prediction)

#app.run()

