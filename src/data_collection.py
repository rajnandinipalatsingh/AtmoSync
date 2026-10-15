"""
AtmoSync - Data Collection Module

Purpose:
    Load and perform basic inspection of the raw microclimate dataset.

The raw dataset is not modified in this module.
"""

from pathlib import Path
import pandas as pd


def load_dataset(file_path):
    """
    Load the raw CSV dataset.

    Parameters
    ----------
    file_path : str or Path
        Location of the CSV file.

    Returns
    -------
    pandas.DataFrame
        Loaded dataset.
    """

    # Convert the supplied path into a Path object
    file_path = Path(file_path)

    # Read the CSV file
    df = pd.read_csv(file_path)

    return df


def inspect_dataset(df):
    """
    Display basic information about the dataset.
    """

    print("=" * 60)
    print("DATASET SHAPE")
    print("=" * 60)

    print(f"Rows    : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())