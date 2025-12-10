"""Helper utilities for downloading NYC 311 data through the Socrata API."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DATASET_ID = "erm2-nwe9"
BASE_URL = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json"
DEFAULT_LIMIT = 25000 
MAX_LIMIT = 50000
REQUEST_TIMEOUT = 120 
MAX_RETRIES = 3
RETRY_DELAY = 2 


def _build_params(year: int, limit: int, offset: int) -> Dict[str, Any]:
    """Create Socrata query parameters for the target year and page."""
    start = f"{year}-01-01T00:00:00"
    end = f"{year}-12-31T23:59:59"
    where_clause = f"created_date between '{start}' and '{end}'"
    return {
        "$limit": limit,
        "$offset": offset,
        "$order": "created_date",
        "$where": where_clause,
    }


def _fetch_page(
    session: requests.Session, params: Dict[str, Any], headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Send a single Socrata request with retry logic and return JSON rows."""
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(
                BASE_URL,
                params=params,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (2 ** attempt) 
                print(f"Request timed out. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(wait_time)
            else:
                print(f"Request failed after {MAX_RETRIES} attempts.")
                raise


def fetch_nyc311_data(
    app_token: Optional[str],
    limit: int = DEFAULT_LIMIT,
    year: int = 2024,
) -> pd.DataFrame:
    """
    Download NYC 311 records for a calendar year and return a DataFrame.

    Parameters
    ----------
    app_token:
        Optional Socrata application token to improve throughput.
    limit:
        Maximum number of rows pulled per request (capped at 50000).
    year:
        Calendar year to collect from the 311 dataset.

    Returns
    -------
    pandas.DataFrame
        All NYC 311 rows for the requested year.
    """
    if limit <= 0 or limit > MAX_LIMIT:
        raise ValueError(f"Limit must be between 1 and {MAX_LIMIT}.")

    records: List[Dict[str, Any]] = []
    offset = 0
    page_count = 0

    # initial status
    print(f"Starting data fetch for year {year}...")
    print(f"Using limit of {limit:,} rows per request.")
    if app_token:
        print("App token detected. Using authenticated requests.")
    else:
        print("No app token. Requests may be slower.")
    print()

    # setting up session with retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    
    # preparing headers for requests
    headers = {}
    if app_token:
        headers["X-App-Token"] = app_token
    
    try:
        while True:
            page_count += 1
            # building SoQL parameters for the current page
            params = _build_params(year=year, limit=limit, offset=offset)
            
            print(f"Fetching page {page_count} (offset {offset:,})...", end=" ", flush=True)
            
            try:
                rows = _fetch_page(session=session, params=params, headers=headers)
            except requests.exceptions.ReadTimeout:
                print(f"\nTimeout on page {page_count}. Consider reducing the limit or trying again later.")
                raise

            if not rows:
                print("No more rows found.")
                break

            records.extend(rows)
            print(f"Received {len(rows):,} rows (total so far: {len(records):,})")
            offset += limit
            
            # stopping if we received fewer rows than the limit, indicating the last page
            if len(rows) < limit:
                print("Last page reached.")
                break
    finally:
        session.close()

    snapshot_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    total_rows = len(records)
    print(f"Snapshot date (UTC): {snapshot_date}")
    print(f"Total rows fetched: {total_rows}")

    # converting JSON records into a DataFrame
    return pd.DataFrame.from_records(records)