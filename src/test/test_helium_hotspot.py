from src.helium.helium_hotspot import HeliumHotspot
from src.helium.logger import main_logger
import src.helium.utils as utils
from datetime import datetime
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
    
    main_logger.info(f'results written to {fname}')
    return

def main() -> None:
    i = 1
    hotspots = open_hotspots('./src/test/hotspots.json')
    n = len(hotspots)
    for h in hotspots:
        main_logger.info(f'Simulation {i} out of {n}')
        test_h = HeliumHotspot(h['lt'], h['lg'], h['e'], h['g'] / 10, 10000, 1)
        avg, interval, link_earnings, knn = test_h.predict_weekly_earnings()
        actual = h['weekly_actual']
        avg_pred_error = np.abs(avg - actual)
        id = h['id']
        main_logger.info(f'Summary:\n\tHotspot: {id}\n\tPrediction (HNT): {avg}\n\tKNN (HNT): {knn}\n\tLink Earnings (HNT): {link_earnings}\n\tActual (HNT): {actual}\n\tBounds (HNT): {interval}\n\tError (HNT) {avg_pred_error}')
        h['avg_pred'] = avg
        h['link_pred'] = link_earnings
        h['knn_pred'] = knn
        h['interval'] = interval
        i += 1
    
    save_test_results(hotspots)
    return

if __name__ == '__main__':
    main()