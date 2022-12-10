import requests
import json

def build_testset(n: int, fname: str) -> None:
    """Build a test dataset."""
    
    keep = []
    keep_ids = []
    states = ['VA', 'MD', 'IL', 'PA', 'OH']
    cursor = ''
    while len(keep) < n:
        ids = []
        response = requests.get('https://helium-api.hotspotty.org/v1/challenges' + cursor).json()
        challenges = response['data']
        cursor = '?cursor=' + response['cursor']
        for r in challenges:
            if r['path'][0]['geocode']['short_country'] != 'US' or r['path'][0]['geocode']['short_state'] not in states: continue
            ids.append(r['path'][0]['challengee'])
        data = requests.post(url='https://etl.hotspotty.org/api/v1/hotspots-lean/', json={'hotspotIds': ids}).json()['data']
        
        for h in data:
            online_status = h['on']
            sync_status = h['sy']
            deny_list_status = h['dl']
            rx_score = h['rru']
            tx_score = h['tru']
            transmit_scale = h['rs']
            if online_status and sync_status and not deny_list_status and rx_score != 0 and tx_score != 0 and transmit_scale != 0:
                keep_ids.append(h['id'])
                keep.append(h)
        
        print(f'Got {len(keep)} entries in test set so far')
    
    data = requests.post(url='https://etl.hotspotty.org/api/v1/hotspots/history/summary-v4-lean/', json={'hotspotIds': keep_ids}).json()['data']
    for h in keep:
        for r in data:
            if h['id'] == r['id']:
                h['weekly_actual'] = r['rewards']['w'] / 100_000_000

    with open(fname, 'w') as f:
        json.dump({'data': keep}, f)
    
    return
        

if __name__ == '__main__':
    build_testset(n=50, fname='./src/test/hotspots.json')