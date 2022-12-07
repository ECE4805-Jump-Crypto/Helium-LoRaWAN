import time
import requests
import datetime
import h3
import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt
import src.helium.utils as utils
import json
import plotly.express as px
import pandas as pd
from datetime import datetime
import sys
import time
import scipy

def open_hotspots(fname: str) -> list:

    with open(fname, 'r') as f:
        hotspots = json.load(f)

    return hotspots['data']

def proximity_knn(hotspot: str, chain_vars: dict) -> None:
    tik = time.time()
    hotspot_details = requests.get(f'https://api.hotspotty.net/api/hotspots/{hotspot}/details').json()['data']
    p1 = [hotspot_details['etl_information']['lat'], hotspot_details['etl_information']['lng']]
    hotspot_res12_loc = hotspot_details['location']
    hotspot_res4_loc = h3.cell_to_parent(hotspot_res12_loc, 4)
    hotspot_px_loc = h3.latlng_to_cell(p1[0], p1[1], chain_vars['poc_v4_parent_res'])
    try:
        response = requests.get(f'https://etl.hotspotty.org/api/v1/hotspots/search-lean/?proximity_hex={hotspot_res12_loc}&limit=500').json()['data']
    except:
        return 0, 0, 0, 0, 0, 0, 0, 0, 0
    
    knn_candidates = [hotspot]
    filtered = []
    for r in response[1:]:
        p2 = [r['lt'], r['lg']]
        p1_p2_dst = utils.get_latlng_distance(p1, p2)
        p2_px_loc = h3.latlng_to_cell(p2[0], p2[1], chain_vars['poc_v4_parent_res'])
        if h3.grid_distance(hotspot_px_loc, p2_px_loc) < chain_vars['poc_v4_exclusion_cells']: continue
        if p1_p2_dst > 20000: continue
        if r['on'] != True: continue
        if r['dl'] != False: continue
        if r['s'] != True: continue
        knn_candidates.append(r['id'])
    
    knn_rewards = []
    
    payload = {
    "hotspotIds": knn_candidates
    }


    headers = {
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }


    rewards = requests.post('https://etl.hotspotty.org/api/v1/hotspots/history/summary-v4-lean/', headers=headers, json=payload).json()['data']
    actual = rewards[0]['rewards']['w'] / 100000000 / 7
    #rewards = requests.get(f'https://etl.hotspotty.org/api/v1/hotspots/history/summary-v2/{hotspot_res4_loc}').json()['data'] # This can be replaced with post for all valid in response
    for reward in rewards:
        #if reward['rewards']['dwa'] >= .001: knn_rewards.append(reward)
        if reward['rewards']['w'] / 7 >= .001: knn_rewards.append(reward)

    valid_rewards = []
   
    
    for candidate in knn_candidates[1:]:
        for reward in knn_rewards:
            if candidate == reward['id']:
                valid_rewards.append(reward['rewards']['w'] / 100000000 / 7)
            if candidate == hotspot: print('SHOULD NOT HAPPEN')

    
    assert actual is not None
    num_data_points = len(valid_rewards)
    if num_data_points == 0:
        print('No valid data points')
        return 0, 0, 0, 0, 0, 0, 0, 0, 0
    
    median_predicted = np.median(valid_rewards)
    mean_predicted = np.mean(valid_rewards)
    low_bound, upper_bound = np.percentile(valid_rewards, [2.5, 97.5])
    tok = time.time()
    print(tok - tik)
    #plt.hist(valid_rewards, bins=num_data_points)
    #plt.axvline(x=actual, color='red', label='actual')
    #plt.axvline(x=mean_predicted, color='gold', label='sample mean')
    #plt.title('valid rewards')
    #plt.show()
    return actual, mean_predicted, median_predicted, low_bound, upper_bound, num_data_points, tok - tik, hotspot_details['name'], scipy.stats.percentileofscore(valid_rewards, actual)

def save_results() -> None:

    with open(fname, 'w') as f:
        json.dump(challenge_info, f)

    return

def open_test_results(fname):

    df = pd.read_json(fname)
    plt.plot(df['num_data_points'], df['error'], '*')
    print(np.mean(df['error']))
    plt.show()
    sys.exit()
    return

if __name__ == '__main__':    
    
    chain_vars = requests.get('https://helium-api.hotspotty.org/v1/vars').json()['data']
    random_hotspots_file = 'src/test/hotspots.json'
    saved_hotspots = open_hotspots(random_hotspots_file)
    #open_test_results('src/test/test_results_12-02-2022-14:59:15.json')
    hotspots = saved_hotspots[:30]
    sample_size = len(hotspots) 
    error_mean = []
    error_median = []
    in_bounds = []
    bound_size = []
    data_points = []
    actuals = []
    percentiles = []
    i = 0

    for hotspot in hotspots:
        time.sleep(1)
        hotspot['size'] = 5
        i += 1
        actual, predicted_mean, predicted_median, low, high, num_data_points, t, n, acutal_percentile = proximity_knn(hotspot['id'], chain_vars)
        if actual <= 0.02: continue
        print(i, '/', sample_size, np.abs((actual - predicted_mean) / actual), np.abs((actual - predicted_median) / actual), actual, predicted_mean, predicted_median, num_data_points)
        data_points.append(num_data_points)
        actuals.append(actual)
        percentiles.append(acutal_percentile)
        error_mean.append(np.abs((actual - predicted_mean) / actual))
        error_median.append(np.abs((actual - predicted_median) / actual))
        in_bounds.append(1 if (low <= actual and actual <= high) else 0)
        bound_size.append(high - low)
        hotspot['error_mean'] = np.abs((actual - predicted_mean) / actual)
        hotspot['error_median'] = np.abs((actual - predicted_median) / actual)
        hotspot['percentile'] = acutal_percentile
        hotspot['num_data_points'] = num_data_points
        hotspot['actual'] = actual
        hotspot['predicted_mean'] = predicted_mean
        hotspot['predicted_median'] = predicted_median
        hotspot['bounds'] = [low, high]
        hotspot['in_bounds'] = 1 if (low <= actual and actual <= high) else 0
        hotspot['sim_time'] = t
        hotspot['name'] = n


    #for line in lines:
    #    line = line.split()
    #    idx = int(line[0])
    #    hotspots[idx]['error'] = float(line[2])
    #    hotspots[idx]['actual'] = float(line[3])
    #    hotspots[idx]['predicted'] = float(line[4])
    #    hotspots[idx]['size'] = 8
    #    error.append(float(line[2]))
    #    
    #print(len(error), np.mean(error))
    

    plotted = [x for x in hotspots if 'error_mean' in x]
    print('Number of simulations done:', sample_size, 'Number of results kept:', len(plotted))
    print('Avg Mean error:', np.mean(error_mean))
    print('Avg Median error:', np.mean(error_median))
    print('Max Mean error:', np.max(error_mean))
    print('Max Median error:', np.max(error_median))
    print('Min Mean error:', np.min(error_mean))
    print('Min Median error:', np.min(error_median))
    print('Percent in bounds:', np.mean(in_bounds))
    print('Mean bound size:', np.mean(bound_size))
    print('Mean HNT uncertainty:', np.mean(bound_size) * 7, 'HNT/week')

    #plt.hist(percentiles)
    #plt.title('Histogram showing number of Hotspots in sample by percentile of actual earnings')
    #plt.xlabel('Percentile of actual earnings')
    #plt.ylabel('Number of hotspots in percentile')
    #plt.show()
#
    #error = np.array(error)
    #percentiles = np.array(percentiles)
    #data_points = np.array(data_points)
#
    #idxs = np.argsort(error)
    #plt.plot(percentiles[idxs], error[idxs], '*')
    #plt.title('kNN error vs percentile of actual earnings')
    #plt.xlabel('Percentile of actual earnings')
    #plt.ylabel('Relative simulation accuracy')
    #plt.show()
#
    #plt.plot(data_points[idxs], error[idxs], '*')
    #plt.title('kNN error vs size of k')
    #plt.xlabel('Percentile of actual earnings')
    #plt.ylabel('Relative simulation accuracy')
    #plt.show()

    now = datetime.now()
    date_time = now.strftime("%m-%d-%Y-%H:%M:%S")	
    df = pd.DataFrame.from_records(plotted)
    save_file_name = f'src/test/test_results_{date_time}.json'
    df.to_json(save_file_name)

    color_scale = [(0, 'green'), (0.5, 'orange'), (1,'red')]

    fig = px.scatter_mapbox(df, 
                            lat="lat", 
                            lon="lng", 
                            color_continuous_scale=color_scale,
                            hover_data=['actual', 'predicted_mean', 'predicted_median'],
                            size='size',
                            color='error_mean',
                            zoom=8, 
                            height=1200,
                            width=1200)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()
    fig.show()

    pass

