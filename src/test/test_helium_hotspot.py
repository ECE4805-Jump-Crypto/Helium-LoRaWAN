from src.helium.helium_hotspot import HeliumHotspot
import src.test.sample_data as sample_data
import src.helium.utils as utils
from datetime import datetime, timedelta
import requests
import numpy as np
import json

def open_hotspots(fname) -> list:
    """Open a list of test hotspots."""

    with open(fname, 'r') as f:
        data = json.load(f)['data']

    return data

def save_test_results(hotspots) -> None:
    """Save the results of a test."""

    now = datetime.now()
    fname = './src/test/results/test_results_' + now.strftime("%m-%d-%Y-%H-%M-%S") + '.json'
    with open(fname, 'w') as f:
        json.dump({'data': hotspots}, f)

def main() -> None:
    hotspots = open_hotspots('./src/test/hotspots.json')
    for h in hotspots:
        test_h = HeliumHotspot(h['lt'], h['lg'], h['e'], h['g'] / 10, 10000, 1)
        avg, interval, link_earnings, knn = test_h.predict_weekly_earnings()
        h['avg_pred'] = avg
        h['link_pred'] = link_earnings
        h['knn_pred'] = knn
        h['interval'] = interval
    
    save_test_results(hotspots)

if __name__ == '__main__':
    main()

#hotspot = HeliumHotspot(sample_data.lat, sample_data.lng, sample_data.agl, sample_data.gain, sample_data.dst, sample_data.srtm_precision)
#hotspot.predict_weekly_earnings()
##hotspot.knn_predict()
#print(hotspot.proximate_knn_prediction, hotspot.proximate_knn_interval)



#for h in hotspot.filtered_hotspots:
#    if h['name'] == 'rich-raspberry-wallaby': print(h)
#for h in hotspot.filtered_hotspots:
#    if h['reason'] != 'too-far': print(h['name'], h['reason'])
