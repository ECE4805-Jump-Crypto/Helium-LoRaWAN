import numpy as np
import requests
from flask_cors import CORS
from flask import Flask, request, jsonify
from src.helium.helium_hotspot import HeliumHotspot
from src.helium.logger import server_logger

app = Flask(__name__)
CORS(app)
hotspot_url = 'http://localhost:5000/api/v1/hotspots'
dst = 20000
srtm_precision = 1

@app.route("/simulation", methods=['GET'])
def run_simulation():
    try:
        response = requests.get(hotspot_url).json()['data']
        hotspot_data = np.array(response[-1])
        lat = hospot_data['Lat']
        lng = hospot_data['Lng']
        agl = hospot_data['elevation']
        gain = data['gain']
        hotspot = HeliumHotspot(lat, lng, agl, gain, dst, srtm_precision)
        prediction, confidence_interval = hotspot.predict_weekly_earnings()
        server_logger.info(f'ran simulation for hotspot lat={lat} lng={lng}')
        return jsonify({'rewards': prediction, 'interval': confidence_interval})
    except Exception as e:
        server_logger.critical('an exception occured')
        server_logger.critical(str(e))  

    return jsonify({'rewards': 0, 'interval': [0, 0]})   


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)