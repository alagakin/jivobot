import logging

logger = logging.getLogger('errors_logger')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/errors.log')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


