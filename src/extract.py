from pathlib import Path
import requests
from .config import RAW_DIR, TLC_BASE_URL, ZONE_LOOKUP_URL


def _download(url: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return path
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with path.open('wb') as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
    return path


def download_month(year: int, month: int) -> Path:
    name = f'yellow_tripdata_{year}-{month:02d}.parquet'
    return _download(f'{TLC_BASE_URL}/{name}', RAW_DIR / name)


def download_zone_lookup() -> Path:
    return _download(ZONE_LOOKUP_URL, RAW_DIR / 'taxi_zone_lookup.csv')
