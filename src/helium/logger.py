import logging

log_format = logging.Formatter('%(asctime)s [%(name)s - %(levelname)s]: %(message)s')
log_level = logging.DEBUG
handler = logging.StreamHandler()
handler.setLevel(log_level)
handler.setFormatter(log_format)

api_logger = logging.getLogger('blockchain_client')
api_logger.addHandler(handler)
api_logger.setLevel(logging.DEBUG)

pysplat_logger = logging.getLogger('pysplat')
pysplat_logger.addHandler(handler)
pysplat_logger.setLevel(logging.DEBUG)

hotspot_logger = logging.getLogger('helium_hotspot')
hotspot_logger.addHandler(handler)
hotspot_logger.setLevel(logging.DEBUG)

server_logger = logging.getLogger('server')
server_logger.addHandler(handler)
server_logger.setLevel(logging.DEBUG)

main_logger = logging.getLogger('main')
main_logger.addHandler(handler)
main_logger.setLevel(logging.DEBUG)
