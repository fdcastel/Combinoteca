import logging
import os

#
# Global settings
#

# Data folder
DATA_FOLDER = './data'

# Database connection string
DB_CONNECTION = f'sqlite:///{DATA_FOLDER}/MegaSena.sqlite'

# Max records to insert into db (0 = no limit)
DB_MAX_RESULTS = 0

# Default log level
LOG_LEVEL=logging.INFO


#
# Global initialization
#

# Configure logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=LOG_LEVEL)
    
# Create data folder
os.makedirs(DATA_FOLDER, exist_ok=True)
