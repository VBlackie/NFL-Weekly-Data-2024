# validation_functions.py

import logging
import pandas as pd


# Validation 1: Check if DataFrame is empty
def validate_not_empty(df: pd.DataFrame, df_name: str) -> bool:
    if df.empty:
        logging.error(f"{df_name} is empty.")
        return False
    return True


# Validation 2: Check for NaN values
def validate_no_nan(df: pd.DataFrame, df_name: str) -> bool:
    if df.isnull().values.any():
        logging.warning(f"{df_name} contains NaN values.")
        return False
    return True


# Validation 3: Check column existence
def validate_columns(df: pd.DataFrame, df_name: str, required_columns: list) -> bool:
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logging.error(f"{df_name} is missing columns: {missing_columns}")
        return False
    return True


# Add more validation functions as needed...


# A wrapper function that runs all validations
def run_validations(df: pd.DataFrame, df_name: str, required_columns: list = None):
    return all([
        validate_not_empty(df, df_name),
        validate_no_nan(df, df_name),
        validate_columns(df, df_name, required_columns) if required_columns else True
    ])
