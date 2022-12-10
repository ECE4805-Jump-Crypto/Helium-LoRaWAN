import argparse
from src.helium.helium_hotspot import HeliumHotspot
from src.helium.logger import main_logger

def parse_args() -> argparse.Namespace:
    """Parse command line arguments. Display help message."""

    parser = argparse.ArgumentParser(description='Main command-line executable for helium hotspot rewards simulation')
    parser.add_argument('--srtm', required=False, type=int, default=1, choices=[1, 3], help='SRTM data precision in Arc-Seconds (should be either 3 or 1). Default to 1.')
    parser.add_argument('--dst', required=False, type=int, default=20000, help='Search radius for hostspot links. Default to 20km. Max is within same res. 4 h3 hex')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--lat', required=True, type=float, help='Hostpot latitude (expressed as decimal)')
    required_args.add_argument('--lng', required=True, type=float, help='Hostpot longitude (expressed as decimal)')
    required_args.add_argument('--agl', required=True, type=float, help='Antenna height (above ground level in meters)')
    required_args.add_argument('--gain', required=True, type=float, help='Antenna gain (directional gain in dBi)')
    return parser.parse_args()


def main() -> None:
    """Main function."""

    args = parse_args()
    main_logger.info('starting simulation')
    try:
        hotspot = HeliumHotspot(args.lat, args.lng, args.agl, args.gain, args.dst, args.srtm)
        ensemble_out, ensemble_interval, link_out, knn_out = hotspot.predict_weekly_earnings()
    except Exception as e:
        main_logger.critical('an exception occured')
        main_logger.critical(str(e))
    
    main_logger.info('simulation successful')
    main_logger.info(f'predicted weekly earnings = {ensemble_out}')
    main_logger.info(f'confidence interval = {ensemble_interval}')
    return


if __name__ == '__main__':
    main()