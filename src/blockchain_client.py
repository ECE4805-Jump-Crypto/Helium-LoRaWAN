import requests
from pprint import pprint
import utils
import h3

class HeliumClient:
    """An API client to interface with the Helium Blockchain."""

    def __init__(self) -> None:
        """Init."""

        self.chain_vars = self.init_chain_vars()
        return
    

    def init_chain_vars(self) -> None:
        """Update chain variables for future consumption."""

        self.chain_vars = requests.get('https://api.helium.io/v1/vars').json()['data']
        return

    def find_nearby_nodes(self, lat: float, lng: float, dst: float) -> list:
        """Return a list of valid nearby link candidates."""

        r = requests.get(f'https://api.helium.io/v1/hotspots/location/distance?lat={lat}&lon={lng}&distance={dst}').json()
        return r['data']
    
    def proximity_filter(self, lat: float, lng: float, nodes: list) -> list:
        """Filter nodes based on blockchain proximity threshold and status."""

        filtered_nodes = []
        rf_candidates = []
        target_location_hex = h3.latlng_to_cell(lat, lng, 11)
        print(f'Performing RF Simulation for node in res 11 hex: {target_location_hex}')
        for node in nodes:
            node_location_hex = h3.latlng_to_cell(node['lat'], node['lng'], 11)
            node_status = node['status']['online']
            if(node_status == 'offline'):
                filtered_nodes.append({'name': node['name'], 'distance': node['distance'], 'reason': 'offline'})
            elif(h3.grid_distance(target_location_hex, node_location_hex) < 8):
                filtered_nodes.append({'name': node['name'], 'distance': node['distance'], 'reason': 'proximity'})
            else:
                rf_candidates.append({'name': node['name'], 'distance': node['distance']})

        if len(filtered_nodes) > 0:
            print('\nThe following nodes were filtered from analysis\n')
            for elem in filtered_nodes:
                pprint(elem, compact=True, width=800)
        if len(rf_candidates) > 0:
            print('\nThe following nodes met RF requirements:\n')
            pprint(rf_candidates)
        return rf_candidates
    




