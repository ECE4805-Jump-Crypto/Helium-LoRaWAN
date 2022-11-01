import argparse
from helium_hotspot import HeliumHotspot

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description='Main command-line executable for helium hotspot rewards simulation')
    parser.add_argument('--srtm', required=False, type=int, default=1, choices=[1, 3], help='SRTM data precision in Arc-Seconds (should be either 3 or 1)')
    parser.add_argument('-o', '--output', required=False, help='Output file to direct summary statistics to')
    parser.add_argument('--rf', required=False, action='store_true', help='Run RF simulation without proceeding')
    parser.add_argument('--dst', required=False, type=int, default=10000, help='Search radius for hostspot links')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--lat', required=True, type=float, help='Hostpot latitude (expressed as decimal)')
    required_args.add_argument('--lng', required=True, type=float, help='Hostpot longitude (expressed as decimal)')
    required_args.add_argument('--agl', required=True, type=float, help='Antenna height (above ground level in meters)')
    required_args.add_argument('--gain', required=True, type=float, help='Antenna gain (expressed in dBi)')
    return parser.parse_args()



def main() -> None:
    """Main function."""

    args = parse_args()
    hotspot = HeliumHotspot(args.lat, args.lng, args.agl, args.gain, args.dst, args.srtm)
    hotspot.update_node_candidates()
    hotspot.rf_analysis()
    hotspot.rf_summary(compare_to = '11ZWzxwiFC3vJ4hmsacs33f2QqQhPSoHvBPe9iHV6sBsErq5sSE')
    if args.rf: return
    hotspot.knn_predict()
    hotspot.deterministic_predict()
    hotspot.ensemble_predict()
    hotspot.mining_rewards_summary()
    return


if __name__ == '__main__':
    main()