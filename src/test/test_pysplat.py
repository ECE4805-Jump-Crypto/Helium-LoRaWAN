import src.test.sample_data as sample_data
from src.pysplat import PySplat
import time

pysplat = PySplat(sample_data.lat, sample_data.lng, sample_data.agl, sample_data.gain, sample_data.srtm_precision)

def test_simulation_time() -> None:
    """Test a single link analysis."""

    tik = time.time()
    results = pysplat.splat_link_analysis(sample_data.nearby_nodes[1:])
    tok = time.time()
    run_time = tok - tik
    print(f'Simulation took {run_time}s')
    return

def test_directional_analysis() -> None:
    """Test a single link analysis."""

    unkown = sample_data.nearby_nodes[-1]
    tx_rssi, rx_rssi, los = pysplat.directional_analysis(unkown)
    print(tx_rssi, rx_rssi, los)
    assert tx_rssi == 0, 'tx_rssi invalid'
    assert rx_rssi == 0, 'rx_rssi invalid'
    assert los == 0, 'los invalid'
    return

if __name__ == '__main__':
    #test_simulation_time()
    test_directional_analysis()