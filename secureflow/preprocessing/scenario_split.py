import pandas as pd
from typing import Tuple, List

HOLDOUT_TEST_SCENARIOS = ["SCN-002", "SCN-005", "SCN-006", "SCN-010"]

def split_by_scenario_holdout(df: pd.DataFrame, scenario_col: str = "scenario_id") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Splits dataset into train/validation set and a scenario-based holdout test set.
    
    Guarantees zero-day attack evaluation by ensuring target attack scenarios in 
    HOLDOUT_TEST_SCENARIOS are absent from training.
    """
    if scenario_col not in df.columns:
        raise ValueError(f"Scenario column '{scenario_col}' not found in dataframe")

    is_holdout = df[scenario_col].isin(HOLDOUT_TEST_SCENARIOS)
    train_val_df = df[~is_holdout].copy()
    test_holdout_df = df[is_holdout].copy()

    return train_val_df, test_holdout_df
