from blockchain_client import HeliumClient
from pysplat import PySplat
import subprocess
import os

class HeliumHotspot:
    """Modelling a Helium Hotspot."""

    def __init__(self, _lat: float, _lng: float, _agl: float, _gain: float, _srtm_precision: int = 3) -> None:
        """Init."""

        # set attrs
        self.lat = _lat
        self.lng = _lng
        self.agl = _agl
        self.gain = _gain
        self.srtm_precision = _srtm_precision
        self.api_client = HeliumClient()
        self.splat = PySplat(self.lat, self.lng, self.agl, self.gain, self.srtm_precision)

        # computed attrs
        self.node_candidates = None
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

        self.node_candidates = self.api_client.find_nearby_nodes(self.lat, self.lng, dst=2000)
        self.node_candidates = self.api_client.proximity_filter(self.lat, self.lng, self.node_candidates)
        return

    def rf_analysis(self) -> None:
        """Filter node candidates by performing an RF analysis to find valid links."""

        self.links = self.splat.get_valid_links()
        self.compute_link_score()
        return
    
    def compute_link_score(self) -> float:
        """Compute and set a link score based on valid links and node activity."""

        pass 
    
    def rf_summary(self) -> None:
        """Display a summary of rf findings for the node under simulation."""

        pass
    
    def knn_predict(self, update_dataset: bool = False) -> None:
        """Generate a knn-based prediction. Update dataset if necessary."""

        pass
    
    def deterministic_predict(self) -> None:
        """Generate prediction based on projections."""

        pass
    
    def ensemble_predict(self) -> None:
        """Generate ensemble prediction."""

        pass