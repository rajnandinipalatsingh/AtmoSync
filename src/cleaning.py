"""
AtmoSync - Data Cleaning Module

Purpose:
    Clean and prepare the microclimate dataset for analysis.
"""

import numpy as np
import pandas as pd


def clean_dataset(df):
    """
    Clean the raw microclimate dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw dataset.

    Returns
    -------
    pandas.DataFrame
        Cleaned dataset.
    """

    # Work on a copy so that the original DataFrame
    # is not accidentally modified.
    df = df.copy()

    # ---------------------------------------------------------
    # 1. Convert timestamp to datetime
    # ---------------------------------------------------------

    df["cdTimestamp"] = pd.to_datetime(
        df["cdTimestamp"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 2. Convert NDVI to numeric
    # ---------------------------------------------------------

    # Invalid text such as "0.38git" becomes NaN.
    df["NDVI"] = pd.to_numeric(
        df["NDVI"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 3. Sort observations
    # ---------------------------------------------------------

    df = df.sort_values(
        by=["Location_ID", "cdTimestamp"]
    )

    # ---------------------------------------------------------
    # 4. Handle invalid NDVI values
    # ---------------------------------------------------------

    # Interpolate NDVI within each monitoring location.
    df["NDVI"] = (
        df.groupby("Location_ID")["NDVI"]
        .transform(
            lambda series:
            series.interpolate(limit_direction="both")
        )
    )

    # ---------------------------------------------------------
    # 5. Remove duplicate records
    # ---------------------------------------------------------

    df = df.drop_duplicates()

    return df