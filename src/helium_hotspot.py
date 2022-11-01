from blockchain_client import HeliumClient
from tabulate import tabulate
from pysplat import PySplat
import subprocess
import os

class HeliumHotspot:
    """Modelling a Helium Hotspot."""

    def __init__(self, _lat: float, _lng: float, _agl: float, _gain: float, _dst: float, _srtm_precision: int) -> None:
        """Init."""

        # set attrs
        self.lat = _lat
        self.lng = _lng
        self.agl = _agl
        self.gain = _gain
        self.dst = _dst
        self.srtm_precision = _srtm_precision
        self.api_client = HeliumClient()
        self.splat = PySplat(self.lat, self.lng, self.agl, self.gain, self.srtm_precision)

        # computed attrs
        self.node_candidates = None
        self.filtered_nodes = None
        self.links = None
        self.num_links = None
        self.link_score = None
        self.tx_density = None
        self.proj_knn_output = None
        self.proj_dt_output = None
        self.proj_ens_output = None
        return
    
    def update_node_candidates(self) -> None:
        """Find and set a list of potential link candidates."""

        self.node_candidates = self.api_client.find_nearby_nodes(self.lat, self.lng, self.dst)
        self.node_candidates, self.filtered_nodes = self.api_client.proximity_filter(self.lat, self.lng, self.node_candidates)
        return

    def rf_analysis(self) -> None:
        """Filter node candidates by performing an RF analysis to find valid links."""

        self.links = self.splat.get_valid_links(self.node_candidates)
        self.compute_link_score()
        return
    
    def compute_link_score(self) -> float:
        """Compute and set a link score based on valid links and node activity."""

        pass 
    
    def rf_summary(self, compare_to: str = None) -> None:
        """Display a summary of rf findings for the node under simulation."""

        summary = []
        actual_witnessed = []
        actual_beaconed = []
        predicted_hotspots_witnessed = 0
        predicted_hotspots_beaconed = 0
        actual_hotspots_witnessed = 0
        actual_hotspots_beaconed = 0

        if compare_to is not None:
            actual_witnessed = self.api_client.get_witnessed_for_hotspot(compare_to)
            actual_beaconed = self.api_client.get_beaconed_for_hotspot(compare_to)
        
        for link in self.links:
            if link['proj_conn_status'] == 'bi-directional':
                predicted_hotspots_beaconed += 1
                predicted_hotspots_witnessed += 1
            elif link['proj_conn_status'] == 'beaconed':
                predicted_hotspots_beaconed += 1
            elif link['proj_conn_status'] == 'witnessed':
                predicted_hotspots_witnessed += 1
            
            if compare_to is not None:
                address = link['address']
                if address in actual_witnessed and address in actual_beaconed:
                    link['actual'] = 'bi-directional'
                    actual_hotspots_witnessed += 1
                    actual_hotspots_beaconed += 1
                elif address in actual_witnessed:
                    link['actual'] = 'witness'
                    actual_hotspots_witnessed += 1
                elif address in actual_beaconed:
                    link['actual'] = 'beacon'
                    actual_hotspots_beaconed += 1
                else:
                    link['actual'] = 'no-connection'
            else:
                link['actual'] = 'unkown'
            
            summary.append([link['name'], link['distance'], link['proj_beacon_rssi'], link['proj_witness_rssi'], link['los'], link['proj_conn_status'], link['actual']])
        
        
        print('\n' + tabulate(summary, headers=['hotspot', 'distance', 'beacon', 'witness', 'los', 'status', 'actual'], tablefmt='orgtbl'))
        if compare_to is not None:
            cumulative_conn = [['actual', actual_hotspots_witnessed, actual_hotspots_beaconed], ['projected', predicted_hotspots_witnessed, predicted_hotspots_beaconed]]
            print('\n' + tabulate(cumulative_conn, headers=['data', '# witnessed', '# beaconed']))
        return
    
    def knn_predict(self, update_dataset: bool = False) -> None:
        """Generate a knn-based prediction. Update dataset if necessary."""

        pass
    
    def deterministic_predict(self) -> None:
        """Generate prediction based on projections."""

        pass
    
    def ensemble_predict(self) -> None:
        """Generate ensemble prediction."""

        pass
    
    def mining_rewards_summary(self) -> None:
        """Generate ensemble prediction."""

        pass