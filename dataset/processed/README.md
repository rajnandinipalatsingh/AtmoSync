# Processed Dataset

This folder contains datasets generated after cleaning and feature engineering.

## Output

`microclimate_cleaned.csv`

The processed dataset is generated from:

`dataset/raw/Microclimate_dataset.csv`

## Processing Includes

- Timestamp conversion
- Numeric conversion of NDVI
- Invalid-value handling
- Duplicate checking
- Missing-value checking
- Time feature extraction
- Environmental feature engineering

The raw dataset is never overwritten.