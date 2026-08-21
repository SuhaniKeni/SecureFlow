import os
import json
import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_RAW_DIR = os.path.join(DATA_DIR, "raw")
DATA_PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
DATA_EXTERNAL_DIR = os.path.join(DATA_DIR, "external")
DATA_META_DIR = os.path.join(DATA_DIR, "metadata")

def test_directory_structure_exists():
    """Verify required data subdirectories exist."""
    assert os.path.exists(DATA_RAW_DIR), "data/raw does not exist"
    assert os.path.exists(DATA_PROCESSED_DIR), "data/processed does not exist"
    assert os.path.exists(DATA_EXTERNAL_DIR), "data/external does not exist"
    assert os.path.exists(DATA_META_DIR), "data/metadata does not exist"

def test_dataset_registry_exists_and_valid():
    """Verify dataset registry JSON files exist and are valid."""
    reg1 = os.path.join(DATA_META_DIR, "dataset_registry.json")
    reg2 = os.path.join(DATA_DIR, "dataset_registry.json")
    
    assert os.path.exists(reg1), "data/metadata/dataset_registry.json missing"
    assert os.path.exists(reg2), "data/dataset_registry.json missing"
    
    with open(reg1, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "datasets" in data
    assert len(data["datasets"]) == 2
    
    for ds in data["datasets"]:
        assert "dataset_name" in ds
        assert "source" in ds
        assert "license" in ds
        assert "download_date" in ds
        assert "actual_file_size_bytes" in ds
        assert "record_count" in ds
        assert "features" in ds
        assert "target" in ds
        assert "intended_use" in ds
        assert "limitations" in ds
        assert ds["actual_file_size_bytes"] > 0
        assert ds["record_count"] > 1000

def test_uci_sms_spam_real_dataset():
    """Verify real UCI SMS Spam Collection file integrity and record count."""
    ext_file = os.path.join(DATA_EXTERNAL_DIR, "SMSSpamCollection_raw.txt")
    proc_file = os.path.join(DATA_PROCESSED_DIR, "uci_sms_spam_clean.csv")
    
    assert os.path.exists(ext_file), "Raw SMS text file missing in data/external"
    assert os.path.exists(proc_file), "Processed SMS CSV missing in data/processed"
    
    df = pd.read_csv(proc_file)
    assert len(df) == 5574, f"Expected exactly 5,574 rows in SMS dataset, found {len(df)}"
    assert "label" in df.columns
    assert "message" in df.columns
    assert "is_spam" in df.columns
    assert df["message"].isnull().sum() == 0

def test_phiusiil_phishing_url_real_dataset():
    """Verify real PhiUSIIL Phishing URL Dataset integrity and record count."""
    ext_file = os.path.join(DATA_EXTERNAL_DIR, "PhiUSIIL_Phishing_URL_Dataset_raw.csv")
    proc_file = os.path.join(DATA_PROCESSED_DIR, "phiusiil_phishing_url_clean.csv")
    
    assert os.path.exists(ext_file), "Raw PhiUSIIL CSV missing in data/external"
    assert os.path.exists(proc_file), "Processed PhiUSIIL CSV missing in data/processed"
    
    df_clean = pd.read_csv(proc_file)
    assert len(df_clean) == 235795, f"Expected exactly 235,795 rows in PhiUSIIL dataset, found {len(df_clean)}"
    assert "URL" in df_clean.columns
    assert "label" in df_clean.columns

def test_data_readme_exists():
    """Verify data/README.md documentation exists and contains expected specs."""
    readme = os.path.join(DATA_DIR, "README.md")
    assert os.path.exists(readme), "data/README.md missing"
    
    with open(readme, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "Verified Public Datasets Registry" in content
    assert "UCI SMS Spam Collection" in content
    assert "PhiUSIIL Phishing URL Dataset" in content
    assert "5,574 rows" in content
    assert "235,795 rows" in content
