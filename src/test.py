from helium_hotspot import HeliumHotspot
import requests

p1 = requests.get('https://api.helium.io/v1/hotspots/name/droll-charcoal-huskie').json()['data'][0]

srtm_precision = 1
hotspot = HeliumHotspot(p1['lat'], p1['lng'], p1['elevation'], p1['gain']/10.0, 5000, srtm_precision)
hotspot.update_node_candidates()
hotspot.rf_analysis()
hotspot.rf_summary(compare_to = p1['address'])