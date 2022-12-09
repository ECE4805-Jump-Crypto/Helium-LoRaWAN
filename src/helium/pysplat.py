from src.helium.logger import pysplat_logger
import src.helium.utils as utils
import numpy as np
import subprocess
import time

class PySplat:
    """Python SPLAT API implementation."""

    def __init__(self, _lat, _lng, _agl, _gain, _srtm_precision) -> None:
        
        # Variable
        self.lat = _lat
        self.lng = _lng
        self.agl = _agl
        self.gain = _gain
        self.srtm_precision = _srtm_precision
        
        # Tuned
        self.name = 'simulation-hotspot'
        self.relative_run_dir = '../..'
        self.splat_run_dir = './src/splat/'
        self.data_file_path = './rf_data/srtm3/'
        self.hd_data_file_path = './rf_data/srtm1/'
        self.bi_directional = 'bi-directional'
        self.tx_only = 'tx-only'
        self.rx_only = 'rx-only'
        self.no_connection = 'no-connection'
        self.rssi_no_connection = -200
        self.los_no_connection = 1000
        self.los_min_clearance = 70
        self.fspl_los = 25
        self.link_freq = 905
        self.simulated_tx_power_db = 27
        self.simulated_cable_loss_db = 0.8
        self.unkown_tx_power_db = 27
        self.unknown_cable_loss_db = 0.8
        self.rssi_threshold_db = -110
        self.los_distance_threshold = 12000
        self.los_clearance_threshold = 10
        self.splat_timeout = 3
        self.run_success = 0
        self.run_timeout = 1
        self.run_unkown_error = 2
        
        # Computed
        self.erp_w = utils.compute_erp_w(self.simulated_tx_power_db, self.gain, self.simulated_cable_loss_db)
        return
    

    def get_valid_links(self, candidates: list) -> tuple:
        """Perform SPLAT! simulation for each candidate."""

        valid = []
        invalid = []
        pysplat_logger.info('changing directories starting splat link analysis')
        utils.cd(self.splat_run_dir)
        tik = time.time()
        for hotspot in candidates:
            tx_predicted_rssi, rx_predicted_rssi, los = self.directional_analysis(hotspot)
            status = self.get_link_status(tx_predicted_rssi, rx_predicted_rssi, los)
            hotspot['proj_tx_rssi'] = tx_predicted_rssi
            hotspot['proj_rx_rssi'] = rx_predicted_rssi 
            hotspot['proj_conn_status'] = status
            hotspot['los_block'] = los
            if status == self.bi_directional: valid.append(hotspot)
            else: invalid.append(hotspot)
        tok = time.time()
        utils.cd(self.relative_run_dir)
        pysplat_logger.info(f'splat link analysis took {tok - tik}s')
        return valid, invalid


    def directional_analysis(self, hotspot: dict) -> tuple:
        """Run bi-directional SPLAT! analysis. Return connection state."""

        utils.write_splat_site_file(self.name, self.lat, self.lng, self.agl)
        utils.write_splat_site_file(hotspot['n'], hotspot['lt'], hotspot['lg'], hotspot['e'])
        point_1 = self.name
        point_2 = hotspot['n']
        point_2_agl = hotspot['e']
        point_2_gain = hotspot['g'] / 10.0
        distance = hotspot['sim_distance']
        los_only = True
        point_1_erp_w = 0
        point_2_erp_w = 0
        tx_rssi = 0
        rx_rssi = 0
        
        if distance < self.los_distance_threshold:
            los_only = False
            point_1_erp_w = self.erp_w
            point_2_erp_w = utils.compute_erp_w(self.unkown_tx_power_db, point_2_gain, self.unknown_cable_loss_db)
        
        receiver_signal_strength = []
        receiver_los_clearance = []
        splat_run_params = [
            ['splat-hd', '-t', point_1, '-r', point_2, '-d', self.hd_data_file_path, '-f', str(self.link_freq), '-erp', str(0), '-metric'],
            ['splat-hd', '-t', point_2, '-r', point_1, '-d', self.hd_data_file_path, '-f', str(self.link_freq), '-erp', str(point_2_erp_w), '-metric']
        ]
        
        for splat_params in splat_run_params:
            path_loss = None
            signal_power_out = self.rssi_no_connection
            los_out = self.los_no_connection
            status = self.run_splat(splat_params)
            if status == self.run_success:
                path_loss, los_out = utils.read_splat_results(splat_params[2], splat_params[4])
            elif status == self.run_unkown_error:
                path_loss = utils.fspl_db(distance, self.link_freq)
                los_out = self.fspl_los
                signal_power_out = utils.link_budget(self.simulated_tx_power_db, self.simulated_cable_loss_db, self.gain - 2.15, path_loss, point_2_gain - 2.15, self.unknown_cable_loss_db)
                return signal_power_out, signal_power_out, self.los_no_connection
            else:
                return self.rssi_no_connection, self.rssi_no_connection, self.los_no_connection
            if splat_params[2] == point_1:
                signal_power_out = utils.link_budget(self.simulated_tx_power_db, self.simulated_cable_loss_db, self.gain - 2.15, path_loss, point_2_gain - 2.15, self.unknown_cable_loss_db)
                if los_out != 0:
                    los_out = los_out - self.agl
            else:
                signal_power_out = utils.link_budget(self.unkown_tx_power_db, self.unknown_cable_loss_db, point_2_gain - 2.15, path_loss, self.gain - 2.15, self.simulated_cable_loss_db)
                if los_out != 0:
                    los_out = los_out - point_2_agl

            receiver_signal_strength.append(signal_power_out)
            receiver_los_clearance.append(los_out)

        tx_rssi = receiver_signal_strength[0]
        rx_rssi = receiver_signal_strength[1]
        min_los_clearance = min(receiver_los_clearance[0], receiver_los_clearance[1])
        utils.clean_splat_files(point_1, point_2)
        return tx_rssi, rx_rssi, min_los_clearance
    

    def run_splat(self, splat_params: list) -> int:
        """Run a single SPLAT analysis as a subprocess. Return True on success."""

        try:
            subprocess.check_output(splat_params, timeout=self.splat_timeout)
        except subprocess.TimeoutExpired as e:
            pysplat_logger.warning('splat analysis timout')
            return self.run_timeout
        except Exception as e:
            print(str(e))
            pysplat_logger.warning('uknown exception occured running splat')
            return self.run_unkown_error
        

        return self.run_success



    def get_link_status(self, tx_rssi: float, rx_rssi: float, los_clearance: float) -> str:
        """
        Determine the status of a potential link.
        Links can be bi_directional, tx_only, rx_only, or no_connection.
        """

        if los_clearance < self.los_clearance_threshold: return self.bi_directional
        elif los_clearance == self.los_no_connection or los_clearance > self.los_min_clearance: return self.no_connection
        elif tx_rssi < self.rssi_threshold_db and rx_rssi < self.rssi_threshold_db: return self.bi_directional
        elif tx_rssi < self.rssi_threshold_db: return self.tx_only
        elif rx_rssi < self.rssi_threshold_db: return self.rx_only

        return self.no_connection 
