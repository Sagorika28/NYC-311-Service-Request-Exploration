"""Helper functions for cleaning NYC 311 service request data."""

from __future__ import annotations

from typing import Optional

import pandas as pd

# required columns for analysis
REQUIRED_COLUMNS = [
    "created_date",
    "closed_date",
    "complaint_type",
    "borough",
    "open_data_channel_type",
    "unique_key",
]


def convert_dates_to_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert created_date and closed_date columns to datetime format.
    
    Parameters
    ----------
    df:
        DataFrame with created_date and closed_date columns as strings.
    
    Returns
    -------
    pd.DataFrame
        DataFrame with date columns converted to datetime.
    """
    df = df.copy()
    
    # converting date columns to datetime
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    df["closed_date"] = pd.to_datetime(df["closed_date"], errors="coerce")
    
    return df


def compute_response_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute response time in days from created_date to closed_date.
    
    Parameters
    ----------
    df:
        DataFrame with created_date and closed_date as datetime columns.
    
    Returns
    -------
    pd.DataFrame
        DataFrame with response_time_days column added.
    """
    df = df.copy()
    
    # computing response time in days
    df["response_time_days"] = (df["closed_date"] - df["created_date"]).dt.total_seconds() / (24 * 3600)
    
    return df


def filter_invalid_rows(
    df: pd.DataFrame,
    require_created_date: bool = True,
    require_closed_date: bool = True,
    require_borough: bool = True,
) -> pd.DataFrame:
    """
    Remove rows with missing required fields or invalid response times.
    
    Parameters
    ----------
    df:
        DataFrame to filter.
    require_created_date:
        If True, drop rows with missing created_date.
    require_closed_date:
        If True, drop rows with missing closed_date.
    require_borough:
        If True, drop rows with missing borough.
    
    Returns
    -------
    pd.DataFrame
        Filtered DataFrame with invalid rows removed.
    """
    df = df.copy()
    initial_count = len(df)
    
    # filtering rows with missing required dates
    if require_created_date:
        df = df[df["created_date"].notna()]
    if require_closed_date:
        df = df[df["closed_date"].notna()]
    if require_borough:
        df = df[df["borough"].notna()]
    
    # removing rows with negative or zero response times (data entry errors)
    if "response_time_days" in df.columns:
        df = df[df["response_time_days"] > 0]
    
    removed = initial_count - len(df)
    if removed > 0:
        print(f"Removed {removed:,} rows with missing required fields or invalid response times.")
        print(f"Remaining rows: {len(df):,}")
    
    return df


def standardize_channel_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize open_data_channel_type into three values: Phone, Web, App.
    
    Parameters
    ----------
    df:
        DataFrame with open_data_channel_type column.
    
    Returns
    -------
    pd.DataFrame
        DataFrame with standardized channel types.
    """
    df = df.copy()
    
    # mapping channel types to standardized values
    channel_mapping = {
        "PHONE": "Phone",
        "ONLINE": "Web",
        "UNKNOWN": "Web",  # treating unknown as web
        "MOBILE": "App",
        "OTHER": "Web",  # treating other as web
    }
    
    # standardizing channel types
    df["open_data_channel_type"] = df["open_data_channel_type"].str.upper().str.strip()
    df["open_data_channel_type"] = df["open_data_channel_type"].map(channel_mapping).fillna("Web")
    
    # checking value counts for verification
    print("\nChannel type distribution after standardization:")
    print(df["open_data_channel_type"].value_counts())
    
    return df


def remove_duplicates(df: pd.DataFrame, key_column: str = "unique_key") -> pd.DataFrame:
    """
    Remove duplicate rows based on unique_key.
    
    Parameters
    ----------
    df:
        DataFrame to deduplicate.
    key_column:
        Column name to use for identifying duplicates.
    
    Returns
    -------
    pd.DataFrame
        DataFrame with duplicates removed.
    """
    df = df.copy()
    initial_count = len(df)
    
    # removing duplicates, keeping first occurrence
    df = df.drop_duplicates(subset=[key_column], keep="first")
    
    removed = initial_count - len(df)
    if removed > 0:
        print(f"\nRemoved {removed:,} duplicate rows based on {key_column}.")
        print(f"Remaining rows: {len(df):,}")
    
    return df


def winsorize_response_time(df: pd.DataFrame, percentile: float = 99.0) -> pd.DataFrame:
    """
    Winsorize response_time_days at the specified percentile to limit outlier influence.
    
    Parameters
    ----------
    df:
        DataFrame with response_time_days column.
    percentile:
        Percentile to use for winsorizing (default 99.0).
    
    Returns
    -------
    pd.DataFrame
        DataFrame with winsorized response_time_days.
    """
    df = df.copy()
    
    if "response_time_days" not in df.columns:
        print("Warning: response_time_days column not found. Skipping winsorization.")
        return df
    
    # computing percentile threshold
    threshold = df["response_time_days"].quantile(percentile / 100)
    
    # counting how many values will be winsorized
    above_threshold = (df["response_time_days"] > threshold).sum()
    
    # winsorizing values above the threshold
    df["response_time_days"] = df["response_time_days"].clip(upper=threshold)
    
    if above_threshold > 0:
        print(f"\nWinsorized {above_threshold:,} values at {percentile}th percentile ({threshold:.2f} days).")
    
    return df


def select_top_complaint_types(
    df: pd.DataFrame,
    n_top: int = 10,
    min_count: Optional[int] = None,
) -> pd.DataFrame:
    """
    Keep only the top N complaint types by volume for reliable within-category comparisons.
    
    Parameters
    ----------
    df:
        DataFrame with complaint_type column.
    n_top:
        Number of top complaint types to keep.
    min_count:
        Minimum count threshold. If provided, keeps all types with at least this many records.
    
    Returns
    -------
    pd.DataFrame
        DataFrame filtered to top complaint types.
    """
    df = df.copy()
    initial_count = len(df)
    
    # counting complaint types
    complaint_counts = df["complaint_type"].value_counts()
    
    if min_count is not None:
        # keeping all types with at least min_count records
        top_types = complaint_counts[complaint_counts >= min_count].index.tolist()
    else:
        # keeping top N types
        top_types = complaint_counts.head(n_top).index.tolist()
    
    # filtering to top complaint types
    df = df[df["complaint_type"].isin(top_types)]
    
    removed = initial_count - len(df)
    print(f"\nFiltered to top complaint types:")
    print(f"  Kept {len(top_types)} complaint types")
    print(f"  Removed {removed:,} rows from other complaint types")
    print(f"  Remaining rows: {len(df):,}")
    print(f"\nTop complaint types:")
    for complaint_type in top_types:
        count = complaint_counts[complaint_type]
        print(f"  - {complaint_type}: {count:,} records")
    
    return df


def clean_nyc311_data(
    df: pd.DataFrame,
    winsorize_percentile: float = 99.0,
    top_complaint_types: Optional[int] = None,
    min_complaint_count: Optional[int] = None,
) -> pd.DataFrame:
    """
    Apply all cleaning steps to NYC 311 data in the correct order.
    
    Parameters
    ----------
    df:
        Raw DataFrame from API.
    winsorize_percentile:
        Percentile for winsorizing response times (default 99.0).
    top_complaint_types:
        Number of top complaint types to keep. If None, keeps all.
    min_complaint_count:
        Minimum count for complaint types. If provided, overrides top_complaint_types.
    
    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame ready for analysis.
    """
    print("Starting data cleaning process...")
    print(f"Initial row count: {len(df):,}\n")
    
    # step 1: convert dates to datetime
    print("Step 1: Converting dates to datetime...")
    df = convert_dates_to_datetime(df)
    
    # step 2: compute response time
    print("Step 2: Computing response time...")
    df = compute_response_time(df)
    
    # step 3: filter invalid rows
    print("Step 3: Filtering invalid rows...")
    df = filter_invalid_rows(df)
    
    # step 4: standardize channel types
    print("Step 4: Standardizing channel types...")
    df = standardize_channel_type(df)
    
    # step 5: remove duplicates
    print("Step 5: Removing duplicates...")
    df = remove_duplicates(df)
    
    # step 6: winsorize response times
    print(f"Step 6: Winsorizing response times at {winsorize_percentile}th percentile...")
    df = winsorize_response_time(df, percentile=winsorize_percentile)
    
    # step 7: select top complaint types (if requested)
    if top_complaint_types is not None or min_complaint_count is not None:
        print("Step 7: Selecting top complaint types...")
        df = select_top_complaint_types(df, n_top=top_complaint_types, min_count=min_complaint_count)
    else:
        print("Step 7: Keeping all complaint types...")
    
    print(f"\nCleaning complete!")
    print(f"Final row count: {len(df):,}")
    
    return df