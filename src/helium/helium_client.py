from requests.adapters import HTTPAdapter, Retry
from src.helium.logger import api_logger
import src.helium.utils as utils
import requests
import urllib3
import time
import sys
import h3

class HeliumClient:
    """An API client to interface with the Helium Blockchain."""

    def __init__(self) -> None:
        """Init."""

        # set attr
        self.max_call_retries = 5
        self.max_request_retries = 3
        self.backoff_factor = 3
        self.deny_sleep_time = 30
        self.forcelist = [403, 404, 429, 500, 502, 503, 504]
        self.etl_sleep_time = 2
        self.user_agent_header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
        self.session = requests.Session()
        self.update_session()
        return
    
    
    def update_session(self) -> None:
        """Set session parameters for future api requests."""

        retry = Retry(total=self.max_call_retries, backoff_factor=self.backoff_factor, status_forcelist=self.forcelist, raise_on_redirect=True)
        self.session.mount('https://', HTTPAdapter(max_retries=retry))
        return

    
    def api_etl_call(self, url: str) -> dict:
        """Make a call to the url, and perform error handling. Return JSON"""

        retries = 0
        while retries < self.max_request_retries:
            try:
                response = self.session.get(url).json()
            except requests.exceptions.RetryError as e:
                api_logger.warning('max api retries exceeded')
            except requests.exceptions.JSONDecodeError as e:
                api_logger.error('JSON Decode Error')
                break
            except Exception as e:
                api_logger.error('unexpected error occured fetching api')
                break
            else:
                return response
            
            api_logger.warning(f'api did not response: sleeping for {self.deny_sleep_time}')
            time.sleep(self.deny_sleep_time)
            retries += 1

        api_logger.critical('api denied all retries')
        return {}

    
    def get_etl_rewards_summary(self, hotspot_ids: list) -> list:
        """Get a reward summary for a list of hotspots."""

        url = 'https://etl.hotspotty.org/api/v1/hotspots/history/summary-v4-lean/'
        payload = {'hotspotIds': hotspot_ids}
        header = {'Content-Type': 'application/json', 'User-Agent': self.user_agent_header['User-Agent']}
        rewards = []
        success = False
        retry_count = 0
        while not success and retry_count < self.max_call_retries:
            response = requests.post(url, headers=header, json=payload)
            if response.status_code == 200:
                try:
                    response = response.json()    
                    rewards = response['data']
                except requests.exception.JSONDecodeError as e:
                    self.api_logger.critical('Got JSON decode error from summary rewards request')
                except:
                    self.api_logger.error('Could not access rewads data from rewards summary response')
                else:
                    success = True
                    break
            else:
                self.api_logger.warnings(f'got status code response {response.status_code}, trying agian')
                time.sleep(self.etl_sleep_time)
            retry_count += 1
        
        return rewards
    
    
    def get_etl_witness_summary(self, hotspot_ids: list) -> list:
        """Get a reward summary for a list of hotspots."""

        url = 'https://etl.hotspotty.org/api/v1/hotspots/witnesses-lean/'
        payload = {'hotspotIds': hotspot_ids}
        header = {'Content-Type': 'application/json', 'User-Agent': self.user_agent_header['User-Agent']}
        rewards = []
        success = False
        retry_count = 0
        while not success and retry_count < self.max_call_retries:
            response = requests.post(url, headers=header, json=payload)
            if response.status_code == 200:
                try:
                    response = response.json()    
                    rewards = response['data']
                except requests.exception.JSONDecodeError as e:
                    self.api_logger.critical('Got JSON decode error from summary witness request')
                except:
                    self.api_logger.error('Could not access rewads data from summary witness response')
                else:
                    success = True
                    break
            else:
                self.api_logger.warnings(f'got status code response {response.status_code}, trying agian')
                time.sleep(self.etl_sleep_time)
            retry_count += 1
        return rewards
    
       
    def get_chain_vars(self) -> dict:
        """Update chain variables for future consumption."""

        url = 'https://api.helium.io/v1/vars'
        response = self.api_etl_call(url)
        return response['data']
        

    def get_etl_poc_events(self, hotspot_id: str, stop_time: int, limit: int) -> list:

        events = []
        url = f'https://api.helium.io/v1/hotspots/{hotspot_id}/roles?filter_types=poc_receipts_v2'
        cursor = ''
        min_time = time.time()
        while min_time > stop_time:
            try:
                response = requests.get(url + cursor).json()
                time.sleep(self.etl_sleep_time)
                poc_events = response['data']
            except KeyError as e:
                self.api_logger.info('got key error in etl poc events')
                return events
            for poc_event in poc_events:
                min_time = poc_event['time']
                if min_time < stop_time: break
                if poc_event['role'] == 'challengee': events.append(poc_event)
            if len(events) > limit: break
            try:
                cursor = '&cursor=' + response['cursor']
            except:
                return events
    
        return events
        
    
    def find_nearby_hotspots(self, proximity_hex: str) -> list:
        """Return a list of valid nearby link candidates. Max of 1000 hotspots are returned"""

        proximity_hex_res = utils.get_hex_res(proximity_hex)
        if(proximity_hex_res > 12):
            api_logger.warning('given proximity hex resolution is not correct. Must be resolution 12')
            api_logger.warnings('getting res 12 hex')
            proximity_hex = utils.hex_to_parent_res12(proximity_hex)
        elif(proximity_hex_res < 12):
            api_logger.critical('given proximity hex resolution is too low. Must be resolution 12')
            return []
        
        url = f'https://etl.hotspotty.org/api/v1/hotspots/search-lean/?proximity_hex={proximity_hex}&limit=1000'
        response = self.api_etl_call(url)
        return response['data']
    

    def get_witnessed_for_hotspot(self, address: str) -> list:
        """Get a list of hotspots that the address witnessed over the last 5 days."""

        url = f'https://api.helium.io/v1/hotspots/{address}/witnessed'
        response = self.api_call(url)
        witnessed_nodes = response['data']
        witnessed = [node['address'] for node in witnessed_nodes]
        return witnessed
    
    def get_witnesses_for_hotspot(self, address: str) -> list:
        """Get a list of hotspots that were witnessed by the address over the last 5 days."""

        url = f'https://api.helium.io/v1/hotspots/{address}/witnesses'
        response = self.api_call(url)
        beaconed_nodes = response['data']
        beaconed = [node['address'] for node in beaconed_nodes]
        return beaconed_nodes
    
    def get_hotspot(self, address: str) -> dict:
        
        url = f'https://api.helium.io/v1/hotspots/{address}'
        response = self.api_call(url)
        return response['data']

    def get_blockchain_challenges(self, min_number: int) -> list:
        """Return a list of at least min_number challenge receipts."""

        min_number = min(min_number, 10e3)
        challenges = []
        url = 'https://api.helium.io/v1/challenges'
        cursor = ''

        while len(challenges) < min_number:
            api_logger.info(f'got {len(challenges)} challenges')
            response = self.api_call(url + cursor)
            challenges.extend(response['data'])
            cursor = '?cursor=' + response['cursor']

        return challenges

    def get_hotspot_poc_roles(self, address: str) -> list:
        """Get POC activity for a hotspot."""
        
        filter_types = '?filter_types=poc_receipts_v2'
        url = f'https://api.helium.io/v1/hotspots/{address}/roles' 
        response = self.api_call(url + filter_types)
        if len(response['data']) == 0: 
            response = self.api_call(url + '?cursor=' + response['cursor'])
        return response['data']

    def get_transaction_data(self, hash: str) -> dict:
        """Return a single transaction from its hash."""

        url = f'https://api.helium.io/v1/transactions/{hash}'
        response = self.api_call(url)
        return response['data']

    def get_transaction_data(self, hash: str) -> dict:
        """Return a single transaction from its hash."""

        url = f'https://api.helium.io/v1/transactions/{hash}'
        response = self.api_call(url)
        return response['data']


    def __del__(self):
        self.session.close()

