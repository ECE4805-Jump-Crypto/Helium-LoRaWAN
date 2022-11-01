import numpy as np
import subprocess
import time
import os

def read_splat_rssi(p1: str, p2: str, rx_gain: float) -> tuple:
    """Read the results of SPLAT! simulation and return rssi."""

    filename = p1 + '-to-' + p2 + '.txt'
    rssi_dbm = -1
    los = False 
    los_height = -1
    with open(filename, 'r', errors='ignore') as f:
        lines = f.readlines()
        for line in lines:
            if line.find('Signal power level') != -1:
                rssi_dbm = float(line.split()[-2])
            elif line.find('No obstructions to LOS path') != -1:
                los = True
            elif los == False and line.find('Antenna at') != -1:
                los_height = float(line.split()[-3])
                break

    return rssi_dbm + rx_gain, los_height

def clean_dir(p1: str, p2: str) -> None:
    """Clean up SPLAT! files."""

    os.remove(p1 + '-site_report.txt')
    os.remove(p1 + '-to-' + p2 + '.txt')
    os.remove(p2 + '-site_report.txt')
    os.remove(p2 + '-to-' + p1 + '.txt')
    os.remove(p2 + '.qth')
    return


class PySplat:
    """Python SPLAT API implementation."""

    def __init__(self, _lat, _lng, _agl, _gain, _srtm_precision) -> None:
        
        self.lat = _lat
        self.lng = _lng
        self.agl = _agl
        self.gain = _gain
        self.name = 'simulation-node'
        self.miner_tx_power = 27
        self.hd_data_threshold = 10000
        self.unknown_node_tx_power = 27
        self.unknown_node_cable_loss = 0.8
        self.cable_loss_tx = 0.8
        self.cable_loss_rx = 0.8
        self.rssi_witness_threshold = -100
        self.rssi_beacon_threshold = -80
        self.data_file_path = './rf_data/srtm3/'
        self.hd_data_file_path = './rf_data/srtm1/'
        self.srtm_precision = _srtm_precision
        self.erp_w = self.compute_erp_w(self.miner_tx_power, self.gain, self.cable_loss_tx)
        return

    def compute_erp_w(self, tx_power, gain, cable_loss_tx) -> float:
        """Comptue ERP in watts."""

        eirp_dbm = tx_power + gain - cable_loss_tx
        erp_dbm = eirp_dbm - 2.15
        erp_w = 10**((erp_dbm - 30)/10)
        return erp_w

    def write_site_file(self, name: str, lat: float, lng: float, agl: float) -> None:
        """Write a *.qth file to be used in SPLAT! simulation."""

        content = [
            name,
            str(lat),
            str(lng*-1),
            str(agl) + 'm'
        ]
        with open(name + '.qth', 'w') as f:
            f.write("\n".join(content))
        return
    

    def get_valid_links(self, candidates: list) -> list:
        """Perform SPLAT! simulation for each candidate"""

        print('Conducting RF analysis...')
        valid = []
        self.write_site_file(self.name, self.lat, self.lng, self.agl)
        tik = time.time()
        for node in candidates:
            status = ''
            beacon, witness, los = self.run_bi_direction(node)
            if los < 5: status = 'bi-directional'
            elif beacon > self.rssi_beacon_threshold and witness < self.rssi_witness_threshold: status = 'witness'
            elif witness > self.rssi_witness_threshold and beacon < self.rssi_beacon_threshold: status = 'beacon'
            else: status = 'no-connection'
            node['proj_beacon_rssi'] = beacon
            node['proj_witness_rssi'] = witness
            node['proj_conn_status'] = status
            node['los'] = los
            valid.append(node)
        tok = time.time()
        
        print(f'RF analysis took {tok - tik}s')
        return sorted(valid, key = lambda link: link['los'])


    def run_bi_direction(self, node: dict) -> tuple:
        """Run bi-directional SPLAT! analysis. Return connection state."""

        self.write_site_file(node['name'], node['lat'], node['lng'], node['elevation'])
        p1 = self.name
        p2 = node['name']
        p2_gain = node['gain'] / 10.0
        erp_w = self.compute_erp_w(self.unknown_node_tx_power, p2_gain, self.unknown_node_cable_loss)
        p1_p2_rssi = 0
        p2_p1_rssi = 0

        if node['distance'] < self.hd_data_threshold:
            try:
                subprocess.check_output(['splat-hd', '-t', p1, '-r', p2, '-d', self.hd_data_file_path, '-erp', str(self.erp_w), '-metric'], timeout=5)
            except subprocess.TimeoutExpired as e:
                p1_p2_rssi = -200
            try:
                subprocess.check_output(['splat-hd', '-t', p2, '-r', p1, '-d', self.hd_data_file_path, '-erp', str(erp_w), '-metric'], timeout=5)
            except subprocess.TimeoutExpired as e:
                p2_p1_rssi = -200
        else: 
            try:
                subprocess.check_output(['splat', '-t', p1, '-r', p2, '-d', self.data_file_path, '-erp', str(self.erp_w), '-metric'], timeout=5)
            except subprocess.TimeoutExpired as e:
                p1_p2_rssi = -200
            try:
                subprocess.check_output(['splat', '-t', p2, '-r', p1, '-d', self.data_file_path, '-erp', str(erp_w), '-metric'], timeout=5)
            except subprocess.TimeoutExpired as e:
                p2_p1_rssi = -200
        
        if p1_p2_rssi != -200: p1_p2_rssi, los_height_p1 = read_splat_rssi(p1, p2, p2_gain)
        if p2_p1_rssi != -200: p2_p1_rssi, los_height_p2 = read_splat_rssi(p2, p1, self.gain)
        clean_dir(p1, p2)
        if los_height_p1 != -1:
            los_height_p1 = los_height_p1 - self.agl 
        if los_height_p2 != -1:
            los_height_p2 = los_height_p2 - node['elevation']
        return p1_p2_rssi, p2_p1_rssi, min(los_height_p1, los_height_p2)