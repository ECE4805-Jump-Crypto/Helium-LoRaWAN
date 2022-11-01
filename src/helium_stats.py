import time
import requests
import datetime
import numpy as np
import pandas as pd 
from pprint import pprint
import matplotlib.pyplot as plt

def main() -> None:
    """Main."""

    lat = 41.8974
    lng = -87.6433
    dst = 10000

    map_query = f'http://maps.google.com/maps?z=12&t=m&q=loc:{lat}+{lng}'
    print(f'Plotting distribution of rewards in 10k radius from {map_query}')
    
    r = requests.get(f'https://api.helium.io/v1/hotspots/location/distance?lat={lat}&lon={lng}&distance={dst}').json()['data']
    addr_keep = ''
    rewards = []
    i = 0
    for candidate in r:
        if(candidate['status']['online'] == 'online'):
            i = i + 1
            addr = candidate['address']
            if i == 1:
                addr_keep = candidate['address']
            time_sleep = 0.1
            time.sleep(time_sleep)
            r = requests.get(f'https://api.helium.io/v1/hotspots/{addr}/rewards/sum?min_time=-7%20day&max_time=2022-10-28T00%3A00%3A00.000Z')
            while r.status_code != 200:
                print(i)
                time_sleep = time_sleep * 2
                time.sleep(time_sleep)
                r = requests.get(f'https://api.helium.io/v1/hotspots/{addr}/rewards/sum?min_time=-7%20day&max_time=2022-10-28T00%3A00%3A00.000Z')
                
            rewards.append(r.json()['data']['sum'])
    
    time.sleep(1)
    pprint(requests.get(f'https://api.helium.io/v1/hotspots/{addr_keep}/rewards/sum?min_time=-7%20day&max_time=2022-10-28T00%3A00%3A00.000Z').json())
    plt.hist(rewards, bins='auto')
    plt.plot(0.89, 30)
    plt.xlabel('Cumulative rewards in last 7 days')
    plt.ylabel('Number of hotspots')
    plt.title('Histogram showing distribution of mining rewards in 10k radius')
    plt.show()


    




if __name__ == '__main__':
    main()