import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = Path(os.getenv('RAW_DIR', BASE_DIR / 'data' / 'raw'))
PROCESSED_DIR = Path(os.getenv('PROCESSED_DIR', BASE_DIR / 'data' / 'processed'))
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://taxi:taxi@localhost:5432/taxi_dw')
TLC_BASE_URL = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
ZONE_LOOKUP_URL = 'https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv'
