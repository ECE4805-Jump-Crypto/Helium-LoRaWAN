from src.helium.helium_client import HeliumClient
from src.helium.logger import hotspot_logger
from datetime import datetime, timedelta
from src.helium.pysplat import PySplat
import src.helium.utils as utils
import numpy as np

class HeliumHotspot:
    """Modeling a Helium Hotspot."""

    def __init__(self, _lat: float, _lng: float, _agl: float, _gain: float, _dst: float, _srtm_precision: int) -> None:
        """Init."""

        # set attrs
        self.lat = _lat
        self.lng = _lng
        self.agl = _agl
        self.gain = _gain
        self.dst = _dst
        self.srtm_precision = _srtm_precision
        self.bone_per_hnt = 100_000_000
        self.poc_reward_units_per_week = 30287999
        self.hnt_per_epoch = 1736.1111
        self.epoch_per_week = 336
        self.witness_hnt_dist = 0.489
        self.challenge_hnt_dist = 0.122
        self.max_rf_analysis = 25
        self.witness_hnt_per_week = self.hnt_per_epoch * self.epoch_per_week * self.witness_hnt_dist
        self.challenge_hnt_per_week = self.hnt_per_epoch * self.epoch_per_week * self.challenge_hnt_dist
        
        # dependent attrs
        self.api_etl_client = HeliumClient()
        self.chain_vars = self.api_etl_client.get_chain_vars()
        self.splat = PySplat(self.lat, self.lng, self.agl, self.gain, self.srtm_precision)

        # prediction attrs
        self.knn_k = None
        self.proximate_knn_prediction = None
        self.proximate_knn_interval = None
        self.poc_tx_reward_units = None
        self.valid_links = None
        self.num_valid_links = None
        self.invalid_links = None
        self.num_invalid_links = None
        self.link_earnings = None
        self.link_earnings_prediction = None
        self.link_earnings_interval = None
        self.ensemble_prediction = None
        self.ensemble_interval = None

        # computed attrs
        self.poc_exclusion_res = self.chain_vars['poc_v4_parent_res']
        self.poc_exclusion_limit = self.chain_vars['poc_v4_exclusion_cells']
        self.poc_exclusion_hex = utils.latlng_to_hex(self.lat, self.lng, self.poc_exclusion_res)
        self.res_4_hex = utils.latlng_to_hex(self.lat, self.lng, 4)
        self.res_12_hex = utils.latlng_to_hex(self.lat, self.lng, 12)
        self.nearby_hotspots = None
        self.filtered_hotspots = None
        self.rf_candidates = None
        self.knn_candidates = None
        return
    
    
    def predict_weekly_earnings(self) -> tuple:
        """Predict hotspot average weekly earnings."""

        self.find_nearby_hotspots()
        self.filter_knn_hotspots()
        self.filter_link_candidates()
        self.filter_link_status()       
        self.compute_link_earnings()
        self.link_earnings_predict()
        self.knn_predict()
        self.ensemble_predict()
        return self.ensemble_prediction, self.ensemble_interval, self.link_earnings_prediction, self.proximate_knn_prediction


    def filter_link_status(self) -> None:
        """Run splat analysis."""

        self.valid_links, self.invalid_links = self.splat.get_valid_links(self.rf_candidates)
        self.num_valid_links = len(self.valid_links)
        self.num_invalid_links = len(self.invalid_links)
        hotspot_logger.info(f'SPLAT Analysis Results: {self.num_valid_links} valid links, {self.num_invalid_links} invalid links')
        return

    
    def find_nearby_hotspots(self) -> None:
        """ETL call and update nearby_hotspots."""

        self.nearby_hotspots = self.api_etl_client.find_nearby_hotspots(self.res_12_hex)
        return

    
    def filter_knn_hotspots(self) -> None:
        """First filter for nearby hotspots. Update knn_candidates."""

        valid_hotspots = []
        self.filtered_hotspots = []
        for hotspot in self.nearby_hotspots:
            online_status = hotspot['on']
            sync_status = hotspot['s']
            deny_list_status = hotspot['dl']
            rx_score = hotspot['rru']
            tx_score = hotspot['tru']
            transmit_scale = hotspot['rs']
            lat = hotspot['lt']
            lng = hotspot['lg']
            hotspot['sim_distance'] = utils.get_latlng_distance([self.lat, self.lng], [lat, lng])
            if not self.status_valid(online_status, sync_status, deny_list_status): 
                self.filtered_hotspots.append({'reason': 'offline-sync-denylist', 'hotspot': hotspot['id'], 'name': hotspot['n']})
            elif not self.poc_active(rx_score, tx_score, transmit_scale):
                self.filtered_hotspots.append({'reason': 'no-poc-activity', 'hotspot': hotspot['id'], 'name': hotspot['n']})
            elif not self.within_distance_limit(hotspot['sim_distance']): 
                self.filtered_hotspots.append({'reason': 'too-far', 'hotspot': hotspot['id'], 'name': hotspot['n']})
            else: 
                valid_hotspots.append(hotspot)

        num_nearby = len(self.nearby_hotspots)
        num_kept = len(valid_hotspots)
        hotspot_logger.info(f'there were {num_nearby} hotspots and {num_kept} left after knn-filtering')
        self.knn_candidates = valid_hotspots
        return
    
    
    def filter_link_candidates(self) -> None:
        """Filter one more time for rf analysis. Impose too-close requirements."""

        valid_hotspots = []
        for hotspot in self.knn_candidates:
            lat = hotspot['lt']
            lng = hotspot['lg']
            if self.in_exclusion_limits(lat, lng):
                self.filtered_hotspots.append({'reason': 'too-close', 'hotspot': hotspot['id'], 'name': hotspot['n']})
            else:
                valid_hotspots.append(hotspot)

        num_knn = len(self.knn_candidates)
        num_kept = len(valid_hotspots)
        if num_kept > self.max_rf_analysis:
            num_kept = self.max_rf_analysis
            valid_hotspots = sorted(valid_hotspots, key=lambda h: h['d'])
            valid_hotspots = valid_hotspots[:self.max_rf_analysis]
        hotspot_logger.info(f'there were {num_knn} hotspots and {num_kept} left after rf-filtering')
        self.rf_candidates = valid_hotspots
        return


    def knn_predict(self) -> None:
        """Generate a proximate knn prediction."""

        hotspot_logger.info(f'generating knn prediction')
        self.k = self.num_valid_links
        ids = [hotspot['id'] for hotspot in self.knn_candidates]
        rewards_response = self.api_etl_client.get_etl_rewards_summary(ids)
        witnesses_response = self.api_etl_client.get_etl_witness_summary(ids)
        hnt_rewards, weights = self.build_knn_weights(rewards_response, witnesses_response)  

        low_bound, upper_bound = np.percentile(hnt_rewards, [2.5, 97.5])
        self.proximate_knn_prediction = np.mean(hnt_rewards)
        self.proximate_knn_interval = [low_bound, upper_bound]
        return
    

    def build_knn_weights(self, rewards, witnesses) -> tuple:
        """Weight each reward by its similarity to number of witnesses. Use inverse weighting."""

        n = len(rewards)
        distances = np.zeros(n)
        weights = np.zeros(n)
        hnt_rewards = np.zeros(n)
        total = 0
        i = 0
        for r in rewards:
            for w in witnesses:
                if r['id'] == w['id']:
                    hnt_rewards[i] = r['rewards']['w'] / self.bone_per_hnt
                    distances[i] = np.abs(self.k - w['wO']['v']) + 0.2
                    weights[i] = 1.0 / distances[i]
                    total += weights[i]
                    i += 1

        weights = weights / total
        return hnt_rewards, weights
    
    
    def compute_link_earnings(self) -> None:
        """Compute a list of earnings per valid PoC link."""
    
        if self.num_valid_links == None or self.num_valid_links == 0:
            hotspot_logger.critical('cannot compute link earnings with no valid links')
            return
        
        self.compute_poc_tx_rewards_units()

        now = datetime.now()
        min_time = (now - timedelta(days=7)).timestamp()
        self.link_earnings = []
        total_poc_events = 0
        for link in self.valid_links:
            poc_events = self.api_etl_client.get_etl_poc_events(link['id'], stop_time=min_time, limit=500)
            link['tx_freq'] = len(poc_events)
            link['weekly_witness_reward_units'] = link['tx_freq'] * link['tsrxru']
            link['weekly_witness_hnt'] = self.witness_hnt_per_week * (link['weekly_witness_reward_units'] / self.poc_reward_units_per_week) 
            self.link_earnings.append(link['weekly_witness_hnt'])
            total_poc_events += link['tx_freq']
        
        avg_tx_freq = total_poc_events / self.num_valid_links
        weekly_challenge_reward_units = self.poc_tx_reward_units * avg_tx_freq
        weekly_challenge_hnt = self.challenge_hnt_per_week * (weekly_challenge_reward_units / self.poc_reward_units_per_week)
        self.link_earnings.append(weekly_challenge_hnt)
        return

    def compute_poc_tx_rewards_units(self) -> None:
        """Update tx reward units for beacons."""

        if self.num_valid_links == None or self.num_valid_links == 0:
            hotspot_logger.critical('cannot compute tx rewards units with no valid links')
            return
        
        witness_redundancy = self.chain_vars['witness_redundancy']
        max_witnesses_per_beacon = self.chain_vars['poc_per_hop_max_witnesses']
        decay_rate = self.chain_vars['poc_reward_decay_rate']
        witness_num = min(self.num_valid_links, max_witnesses_per_beacon)
        if witness_num <= witness_redundancy:
            self.poc_tx_reward_units = witness_num / witness_redundancy
        else:
            self.poc_tx_reward_units = 1 + (1 - (decay_rate**(witness_num - witness_redundancy)))
        return


    def link_earnings_predict(self) -> None:
        """Generate a link earnings model prediction."""

        self.link_earnings_prediction = sum(self.link_earnings)
        return

    def ensemble_predict(self) -> None:
        """Generate an ensemble prediction."""


        self.ensemble_prediction = np.mean([self.link_earnings_prediction, self.proximate_knn_prediction])
        self.ensemble_interval = self.proximate_knn_interval
        pass  
    
    def status_valid(self, online: bool, sync: bool, deny_list: bool) -> bool:
        """Return true if hotspot status is valid."""

        return bool(online and sync and (not deny_list))
    
    
    def poc_active(self, rx: float, tx: float, tx_scale: float) -> bool:
        """Return true if hotspot has engaged in PoC activity and has valid tx scale."""

        return bool(rx != 0 and tx != 0 and tx_scale != 0)
    
    
    def within_distance_limit(self, distance: float) -> bool:
        """Return true if distance betwen self and [lat, lng] is within limits."""

        return bool(distance < self.dst)
    
    
    def in_exclusion_limits(self, lat: float, lng: float) -> bool:
        """Return true if hospot is in exclusion limit."""

        hotspot_exclusion_hex = utils.latlng_to_hex(lat, lng, self.poc_exclusion_res)
        exclusion_distance = utils.get_hex_distance(self.poc_exclusion_hex, hotspot_exclusion_hex)
        return bool(exclusion_distance < self.poc_exclusion_limit)
    

    