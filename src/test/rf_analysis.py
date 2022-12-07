from src.blockchain_client import HeliumClient
from collections import Counter
import matplotlib.pyplot as plt
import src.utils as utils
import numpy as np
import json
import requests
import plotly.express as px
import pandas as pd



helium_client = HeliumClient()

def filter_challenges(challenges: list) -> list:
    """Keep US challenges only."""

    filtered = []
    states = ['VA', 'MD', 'OH', 'IL', 'IN']
    for challenge in challenges:
        try:
            if challenge['path'][0]['geocode']['short_country'] == 'US':
                filtered.append(challenge)
        except KeyError:
            continue
    
    print(len(filtered))
    return filtered


def update_challenges(num: int, fname: str) -> None:
    
    challenges = helium_client.get_blockchain_challenges(num)
    with open(fname, 'w') as f:
        json.dump(filter_challenges(challenges), f)
    
    return


def update_hotspots(challenges: list, fname: str) -> None:

    seen = set()
    hotspots = []
    for challenge in challenges:
        address = challenge['path'][0]['challengee']
        if address not in hotspots:
            seen.add(address)
            hotspots.append({
                'address': address,
                'lat': challenge['path'][0]['challengee_lat'],
                'lng': challenge['path'][0]['challengee_lon'],
                'short_state': challenge['path'][0]['geocode']['short_state'],
            })
    
    with open(fname, 'w') as f:
        json.dump(hotspots, f)
    
    return

def open_hotspots(fname: str) -> dict:

    with open(fname, 'r') as f:
        hotspots = json.load(f)

    return hotspots


def open_challenges(fname: str) -> list:
    
    with open(fname, 'r') as f:
        challenges = json.load(f)
    
    return challenges


def save_challenge_info(challenge_info: list, fname: str) -> None:

    with open(fname, 'w') as f:
        json.dump(challenge_info, f)

    return


def display_sample_stats(hotspots: list) -> None:

    print('Number of unique hotspots:', len(set([x['address'] for x in hotspots])))
    print('Number of hotspots by state:', Counter([x['short_state'] for x in hotspots]))
    return

def get_valid_witnessed(hotspot: dict) -> None:

    roles = helium_client.get_hotspot_poc_roles(hotspot['address'])
    witness_roles = [role for role in roles if role['role'] == 'witness']
    total_num_roles = len(witness_roles)
    witnessed = []
    i = 0
    for role in witness_roles:
        transaction_data = helium_client.get_transaction_data(role['hash'])
        challengee = transaction_data['path'][0]['challengee']
        for witness in transaction_data['path'][0]['witnesses']:
            if witness['gateway'] == hotspot['address'] and witness['is_valid'] == True:
                print('HERE')
                witnessed.append(challengee)
        print(i, '/', total_num_roles)
        i += 1

    print(witnessed)
    print((set(witnessed)))
    print(len(set(witnessed)))
    return


if __name__ == '__main__':
    challenge_num = 10000
    random_challenges_file = 'src/test/random_challenges.json'
    random_hotspots_file = 'src/test/random_hotspots_test.json'
    hotspot_coverage_summary_file = 'src/test/random_hotspots.json'
    
    update_challenges(challenge_num, random_challenges_file)
    random_challenges = open_challenges(random_challenges_file)
    update_hotspots(random_challenges, random_hotspots_file)
    hotspots = open_hotspots(random_hotspots_file)
    print(len(hotspots))
    #lats = [x['lat'] for x in hotspots]
    #lngs = [x['lng'] for x in hotspots]
    #fig = px.scatter_mapbox(lat=lats, lon=lngs)
    #fig.show()
    #print(len(hotspots))
    