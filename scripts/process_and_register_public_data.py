import os
import json
import shutil
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DATA_EXTERNAL_DIR = os.path.join(BASE_DIR, "data", "external")
DATA_META_DIR = os.path.join(BASE_DIR, "data", "metadata")
DOCS_DIR = os.path.join(BASE_DIR, "docs", "datasets")

os.makedirs(DATA_RAW_DIR, exist_ok=True)
os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
os.makedirs(DATA_EXTERNAL_DIR, exist_ok=True)
os.makedirs(DATA_META_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

def process_sms_spam_collection():
    """Process UCI SMS Spam Collection dataset."""
    src_file = os.path.join(DATA_RAW_DIR, "sms_spam_zip", "SMSSpamCollection")
    if not os.path.exists(src_file):
        raise FileNotFoundError(f"Missing SMS source file: {src_file}")
        
    ext_dest = os.path.join(DATA_EXTERNAL_DIR, "SMSSpamCollection_raw.txt")
    shutil.copyfile(src_file, ext_dest)
    
    # Read tab-separated SMSSpamCollection
    rows = []
    with open(src_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split("\t", 1)
            if len(parts) == 2:
                rows.append({"label": parts[0], "message": parts[1]})
                
    df = pd.DataFrame(rows)
    raw_csv = os.path.join(DATA_RAW_DIR, "uci_sms_spam_raw.csv")
    df.to_csv(raw_csv, index=False)
    
    proc_csv = os.path.join(DATA_PROCESSED_DIR, "uci_sms_spam_clean.csv")
    # Basic clean: map ham->0, spam->1
    df_clean = df.copy()
    df_clean["is_spam"] = (df_clean["label"] == "spam").astype(int)
    df_clean.to_csv(proc_csv, index=False)
    
    file_size_raw = os.path.getsize(raw_csv)
    file_size_ext = os.path.getsize(ext_dest)
    
    print(f"[+] Processed UCI SMS Spam Collection:")
    print(f"    - Raw file: {ext_dest} ({file_size_ext:,} bytes)")
    print(f"    - Clean CSV: {proc_csv} ({len(df):,} rows)")
    
    return {
        "dataset_name": "UCI SMS Spam Collection",
        "dataset_id": "uci_sms_spam",
        "source": "https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "download_date": "2026-08-21",
        "actual_file_size_bytes": file_size_raw,
        "record_count": len(df),
        "features": ["message"],
        "target": "label (ham/spam) / is_spam (0/1)",
        "intended_use": "Scam-Context NLP Engine training & benchmarking (spam vs ham text baseline classification)",
        "limitations": "Collected in 2012; mobile SMS context. Does not include UPI/payment app specific terms, requiring domain-specific lexicon integration."
    }

def process_phiusiil_phishing_url():
    """Process PhiUSIIL Phishing URL Dataset."""
    src_file = os.path.join(DATA_RAW_DIR, "phiusiil_zip", "PhiUSIIL_Phishing_URL_Dataset.csv")
    if not os.path.exists(src_file):
        raise FileNotFoundError(f"Missing PhiUSIIL source file: {src_file}")
        
    ext_dest = os.path.join(DATA_EXTERNAL_DIR, "PhiUSIIL_Phishing_URL_Dataset_raw.csv")
    if not os.path.exists(ext_dest):
        shutil.copyfile(src_file, ext_dest)
        
    df = pd.read_csv(src_file)
    raw_csv = os.path.join(DATA_RAW_DIR, "phiusiil_phishing_url_raw.csv")
    if not os.path.exists(raw_csv):
        df.to_csv(raw_csv, index=False)
        
    # Processed subset relevant to low-latency payment URL scoring
    key_features = ["URL", "URLLength", "DomainLength", "IsDomainIP", "TLD", "HTTPS", "label"]
    available_features = [c for c in key_features if c in df.columns]
    df_clean = df[available_features].copy()
    proc_csv = os.path.join(DATA_PROCESSED_DIR, "phiusiil_phishing_url_clean.csv")
    df_clean.to_csv(proc_csv, index=False)
    
    file_size_ext = os.path.getsize(ext_dest)
    
    print(f"[+] Processed PhiUSIIL Phishing URL Dataset:")
    print(f"    - Raw file: {ext_dest} ({file_size_ext:,} bytes)")
    print(f"    - Clean CSV: {proc_csv} ({len(df):,} rows, {len(df.columns)} columns)")
    
    return {
        "dataset_name": "PhiUSIIL Phishing URL Dataset",
        "dataset_id": "phiusiil_phishing_url",
        "source": "https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "download_date": "2026-08-21",
        "actual_file_size_bytes": file_size_ext,
        "record_count": len(df),
        "features": list(df.columns)[:10] + [f"... ({len(df.columns)-10} more)"],
        "target": "label (0=legitimate, 1=phishing)",
        "intended_use": "URL / Destination Intelligence Engine feature extraction (lexical, domain, and security indicators)",
        "limitations": "High-dimensional dataset (54 features); light extraction required for low-latency payment gateway scoring."
    }

def generate_registry_and_readme(meta_list):
    """Generate dataset registry files and data/README.md."""
    registry = {"datasets": meta_list}
    
    # Save to data/metadata/dataset_registry.json
    path1 = os.path.join(DATA_META_DIR, "dataset_registry.json")
    with open(path1, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
        
    # Save to data/dataset_registry.json
    path2 = os.path.join(BASE_DIR, "data", "dataset_registry.json")
    with open(path2, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
        
    readme_path = os.path.join(BASE_DIR, "data", "README.md")
    
    content = "# SecureFlow Data Layer Documentation (Stage 5.2)\n\n"
    content += "This directory contains public datasets and metadata registered for SecureFlow.\n\n"
    content += "## Directory Structure\n\n"
    content += "```text\n"
    content += "data/\n"
    content += "├── raw/         # Unmodified downloaded raw dataset files\n"
    content += "├── processed/   # Cleaned, standardized CSVs ready for feature extraction\n"
    content += "├── external/    # Original archived zip/txt datasets from external sources\n"
    content += "├── metadata/    # Dataset registry JSON metadata\n"
    content += "├── dataset_registry.json\n"
    content += "└── README.md    # Data layer documentation\n"
    content += "```\n\n"
    content += "## Verified Public Datasets Registry\n\n"
    
    for item in meta_list:
        content += f"### {item['dataset_name']} (`{item['dataset_id']}`)\n\n"
        content += f"- **Source URL**: [{item['source']}]({item['source']})\n"
        content += f"- **License**: {item['license']}\n"
        content += f"- **Download Date**: {item['download_date']}\n"
        content += f"- **Actual File Size**: {item['actual_file_size_bytes']:,} bytes\n"
        content += f"- **Verified Record Count**: {item['record_count']:,} rows\n"
        content += f"- **Target**: `{item['target']}`\n"
        content += f"- **Features**: `{', '.join(item['features'][:8])}`\n"
        content += f"- **Intended Use**: {item['intended_use']}\n"
        content += f"- **Limitations**: {item['limitations']}\n\n"
        
    content += "---\n"
    content += "## Security & Data Privacy Enforcement\n"
    content += "- **No Real Customer Data**: Zero real financial, UPI, or personal customer data is present.\n"
    content += "- **No Payment Data**: Payment behavior data is NOT created in Stage 5.2 (strictly reserved for Stage 5.3 synthetic database).\n"
    content += "- **No Trained Models**: No ML models are trained in Stage 5.2.\n"
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"[+] Saved dataset registry: {path1}")
    print(f"[+] Saved dataset registry: {path2}")
    print(f"[+] Saved data/README.md: {readme_path}")

if __name__ == "__main__":
    print("=== Processing & Registering Stage 5.2 Public Datasets ===")
    m1 = process_sms_spam_collection()
    m2 = process_phiusiil_phishing_url()
    generate_registry_and_readme([m1, m2])
    print("=== Stage 5.2 Data Ingestion Complete ===")
