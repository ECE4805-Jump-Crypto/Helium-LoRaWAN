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
    

    def init_chain_vars(self) -> dict:
        """Update chain variables for future consumption."""

        return requests.get('https://api.helium.io/v1/vars').json()['data']
        

    def find_nearby_nodes(self, lat: float, lng: float, dst: float) -> list:
        """Return a list of valid nearby link candidates."""

        r = requests.get(f'https://api.helium.io/v1/hotspots/location/distance?lat={lat}&lon={lng}&distance={dst}').json()
        return r['data']
    
    def proximity_filter(self, lat: float, lng: float, nodes: list) -> tuple:
        """Filter nodes based on blockchain proximity threshold and status."""

        print('Pre-filtering nodes based on status and proximity limits')
        filtered_nodes = []
        rf_candidates = []
        poc_v4_parent_res = self.chain_vars['poc_v4_parent_res']
        poc_v4_exclusion_cells = self.chain_vars['poc_v4_exclusion_cells']
        target_location_hex = h3.latlng_to_cell(lat, lng, poc_v4_parent_res)
        for node in nodes:
            node_location_hex = h3.latlng_to_cell(node['lat'], node['lng'], poc_v4_parent_res)
            node_status = node['status']['online']
            if(node_status == 'offline'):
                filtered_nodes.append({'name': node['name'], 'distance': node['distance'], 'reason': 'offline'})
            elif(h3.grid_distance(target_location_hex, node_location_hex) < poc_v4_exclusion_cells):
                filtered_nodes.append({'name': node['name'], 'distance': node['distance'], 'reason': 'proximity'})
            else:
                rf_candidates.append(node)

            
        return rf_candidates, filtered_nodes
    
    def get_witnessed_for_hotspot(self, address: str) -> list:
        """Get a list of hotspots that were witnessed by the address over the last 5 days."""

        r = requests.get(f'https://api.helium.io/v1/hotspots/{address}/witnessed').json()['data']
        witnessed = [node['address'] for node in r]
        return witnessed
    
    def get_beaconed_for_hotspot(self, address: str) -> list:
        """Get a list of hotspots that were beaconed by the address over the last 5 days."""

        r = requests.get(f'https://api.helium.io/v1/hotspots/{address}/witnesses').json()['data']
        beaconed = [node['address'] for node in r]
        return beaconed





