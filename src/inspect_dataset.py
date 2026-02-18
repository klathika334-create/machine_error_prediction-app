# inspect_dataset.py
# This script inspects the dataset to identify column names and structure.

import pandas as pd

# Load the dataset
file_path = "data/Industrial_MultiClass_Dataset_With_Slip.xlsx"
data = pd.read_excel(file_path)

# Print the first few rows and column names
print("Dataset Columns:")
print(data.columns)
print("\nFirst Few Rows:")
print(data.head())
