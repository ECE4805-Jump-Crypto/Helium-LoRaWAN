import src.test.sample_data as sample_data
from src.blockchain_client import HeliumClient

helium_client = HeliumClient()

def test_helium_client_call():
    
    response = helium_client.api_call('https://api.helium.io/v1/vars/block_time')
    assert response != {}
    assert 'data' in response

    response = helium_client.api_call('https://api.helium.io/v1/vars/fdsfjlkd')
    assert response == {}
    return

def test_helium_client_chain_vars():

    chain_vars = helium_client.get_chain_vars()
    assert chain_vars != {}
    assert 'poc_v4_parent_res' in chain_vars
    assert 'poc_v4_exclusion_cells' in chain_vars
    return

def test_helium_client_find_nearby():

    nearby_nodes = helium_client.find_nearby_nodes(lat=sample_data.lat, lng=sample_data.lng, dst=sample_data.dst)
    assert nearby_nodes != []
    assert len(nearby_nodes) > 5
    assert 'lng' in nearby_nodes[0]
    return

def test_helium_client_proximity_filter():
    
    valid, filtered = helium_client.proximity_filter(lat=sample_data.lat, lng=sample_data.lng, nodes=sample_data.nearby_nodes)
    assert len(valid) == 5
    assert len(filtered) == 4
    return

def test_helium_client_get_hotspot():
    
    hotspot = helium_client.get_hotspot(sample_data.address)
    assert 'timestamp_added' in hotspot
    assert hotspot['timestamp_added'] == '2021-08-07T15:48:06.000000Z'
    return

def test_helium_client_get_witnessed():

    hotspot = helium_client.get_hotspot(sample_data.address)
    witnessed = helium_client.get_witnessed_for_hotspot(sample_data.address)
    assert (len(witnessed) > 0 and hotspot['status']['online'] == 'online') or hotspot['status']['online'] != 'online'
    return

def test_helium_client_get_beaconed():

    hotspot = helium_client.get_hotspot(sample_data.address)
    beaconed = helium_client.get_beaconed_for_hotspot(sample_data.address)
    assert (len(beaconed) > 0 and hotspot['status']['online'] == 'online') or hotspot['status']['online'] != 'online'
    return

#api_client = HeliumClient()
#
#n = 25
#
#acc = [0.25035859645817843, 0.5855684368462127, 0.23487031640115086, 0.5471006765511203, 0.2563803105049501, 0.5521743168747257, 2.252162280362764]
#
##p1 = requests.get('https://api.helium.io/v1/hotspots/11ZWzxwiFC3vJ4hmsacs33f2QqQhPSoHvBPe9iHV6sBsErq5sSE').json()['data']
#p = requests.get('https://api.helium.io/v1/hotspots/location/distance?lat=37.232566643994076&lon=-80.41454734731097&distance=1000').json()['data']
#nearby = []
#for p1 in p:
#    if p1['status']['online'] == 'offline': continue
#    
#    url = 'https://api.helium.io/v1/hotspots/' + p1['address'] + '/rewards/sum?min_time=-7%20day&bucket=week'
#    try:
#        actual = requests.get(url).json()['data'][0]['total']
#    except:
#        time.sleep(2)
#        actual = requests.get(url).json()['data'][0]['total']
#    p1['actual'] = actual
#    if p1['actual'] == 0.0:
#        print(p1['name'])
#        continue
#    nearby.append(p1)
#
#print(len(nearby))
#i = 0
#for p in nearby:
#    print(p['name'], p['lat'], p['lng'], p['elevation'], p['gain'], acc[i])
#    i = i + 1
#
#exit
#error = []
#bounds = []
#in_bounds = []
#bound_size = []
#acutals = []
#for p1 in nearby:
#    print(p1['name'])
#    if p1['status']['online'] == 'offline': continue
#    actual = p1['actual']
#    srtm_precision = 1
#    hotspot = HeliumHotspot(p1['lat'], p1['lng'], p1['elevation'], p1['gain']/10.0, 5000, srtm_precision)
#    hotspot.update_node_candidates()
#    hotspot.rf_analysis()
#    hotspot.rf_summary()
#    sim, bounds = hotspot.deterministic_predict()
#    error.append(np.abs(sim - actual) / actual)
#    bound_size.append(bounds[1] - bounds[0])
#    in_bounds.append(1 if actual >= bounds[0] and actual <= bounds[1] else 0)
#
#print('Error')
#print(error)
#print(np.mean(error))
#print(np.max(error))
#print(np.min(error))
#
#print('Bounds')
#print(np.mean(in_bounds))
#print(np.mean(bound_size))
#
