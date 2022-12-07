import numpy as np
import os
import h3

def latlng_to_hex(lat: float, lng: float, res: int) -> str:
    """Convert lat and lng to res12 hex index."""

    return h3.latlng_to_cell(lat, lng, res)


def get_hex_res(hex_idx: str) -> int:
    """Return the resolution of a hex index."""

    return h3.get_resolution(hex_idx)


def hex_to_parent_res12(hex_idx: str) -> str:
    """Convert a hex index to its res 12 parent."""

    return h3.cell_to_parent(hex_idx, 12)


def get_latlng_distance(p1: list, p2: list) -> float:
    """Compute distance in meters between to lat/lng points."""

    return h3.great_circle_distance(p1, p2, unit='m')


def get_hex_distance(a_idx: str, b_idx: str) -> int:
    """Compute the hex distance in between two hex indexes."""

    return h3.grid_distance(a_idx, b_idx)

def cd(dir: str) -> None:
    """Change directories. Used during SPLAT! analysis."""

    os.chdir(dir)
    return

def read_splat_results(p1: str, p2: str) -> tuple:
    """Read the results of SPLAT! simulation and return signal power and los."""

    filename = p1 + '-to-' + p2 + '.txt'
    path_loss = -1
    los = False 
    los_height = 0
    with open(filename, 'r', errors='ignore') as f:
        lines = f.readlines()
        for line in lines:
            if line.find('ITWOM Version 3.0 path loss') != -1:
                path_loss = float(line.split()[-2])
            elif line.find('No obstructions to LOS path') != -1:
                los = True
            elif los == False and line.find('Antenna at') != -1:
                los_height = float(line.split()[-3])
                break

    return path_loss, los_height


def clean_splat_files(p1: str, p2: str) -> None:
    """Clean up SPLAT! files."""

    os.remove(p1 + '-site_report.txt')
    os.remove(p1 + '-to-' + p2 + '.txt')
    os.remove(p2 + '-site_report.txt')
    os.remove(p2 + '-to-' + p1 + '.txt')
    os.remove(p1 + '.qth')
    os.remove(p2 + '.qth')
    return


def link_budget(tx_pow, tx_loss, tx_gain, path_loss, rx_gain, rx_loss) -> float:
    """Compute the link budget in dB."""

    return tx_pow - tx_loss + tx_gain - path_loss + rx_gain - rx_loss


def compute_erp_w(tx_power: float, gain: float, cable_loss_tx: float) -> float:
    """Comptue ERP in watts."""

    eirp_dbm = tx_power + gain - cable_loss_tx
    erp_dbm = eirp_dbm - 2.15
    erp_w = 10**((erp_dbm - 30)/10)
    return erp_w


def write_splat_site_file(name: str, lat: float, lng: float, agl: float) -> None:
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


def db(a: float) -> float:
    """Convert a to decibels."""

    return 20*np.log10(a)


def fspl_db(dst: float, f: float) -> float:
    """Compute fspl and return in db."""

    return db(dst) + db(f) + db((4*np.pi)/299792458.0)


