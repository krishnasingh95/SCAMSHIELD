"""
ScamShield V2 — Dataset Inspection Script
Inspects downloaded datasets WITHOUT executing or visiting any URLs.
"""
import pandas as pd
import hashlib
import os
import json
from datetime import datetime, timezone

BASE = 'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/external'

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def inspect_df(df, url_col=None, label_col=None):
    info = {}
    info['total_rows'] = len(df)
    info['columns'] = list(df.columns)
    info['dtypes'] = {c: str(df[c].dtype) for c in df.columns}
    info['missing_values'] = df.isnull().sum().to_dict()
    info['total_missing'] = int(df.isnull().sum().sum())
    info['duplicate_rows'] = int(df.duplicated().sum())
    
    if url_col and url_col in df.columns:
        info['url_column'] = url_col
        info['unique_urls'] = int(df[url_col].nunique())
        info['duplicate_urls'] = int(df[url_col].duplicated().sum())
    
    if label_col and label_col in df.columns:
        info['label_column'] = label_col
        vc = df[label_col].value_counts().to_dict()
        info['class_distribution'] = {str(k): int(v) for k, v in vc.items()}
        info['unique_label_values'] = sorted([str(x) for x in df[label_col].unique()])
    
    return info

results = {}

# =====================================================================
# 1. URL_Phish_V2 — Dataset.csv
# =====================================================================
print("=" * 60)
print("DATASET 1: URL_Phish_V2")
print("=" * 60)

path1 = f'{BASE}/URL_Phish_V2/Dataset.csv'
size1 = os.path.getsize(path1)
sha1 = sha256_file(path1)
print(f"File: {path1}")
print(f"Size: {size1:,} bytes ({size1/1024/1024:.2f} MB)")
print(f"SHA256: {sha1}")

df1 = pd.read_csv(path1, low_memory=False)
print(f"\nShape: {df1.shape}")
print(f"\nColumns:")
for c in df1.columns:
    print(f"  {c!r:40s} dtype={df1[c].dtype}")

print(f"\nFirst 3 rows:")
print(df1.head(3).to_string())

print(f"\nLast 3 rows:")
print(df1.tail(3).to_string())

# Identify URL and label columns
url_col1 = None
label_col1 = None
for c in df1.columns:
    cl = c.lower()
    if 'url' in cl and url_col1 is None:
        url_col1 = c
    if cl in ('label', 'class', 'phishing', 'is_phishing', 'target', 'status'):
        label_col1 = c

print(f"\nIdentified URL column: {url_col1}")
print(f"Identified Label column: {label_col1}")

if label_col1:
    print(f"\nClass distribution for '{label_col1}':")
    vc = df1[label_col1].value_counts()
    print(vc)

print(f"\nMissing values:")
mv = df1.isnull().sum()
print(mv[mv > 0] if mv.sum() > 0 else "  None")

print(f"\nDuplicate rows: {df1.duplicated().sum()}")
if url_col1:
    print(f"Duplicate URLs: {df1[url_col1].duplicated().sum()}")

info1 = inspect_df(df1, url_col1, label_col1)
info1['file'] = 'Dataset.csv'
info1['size_bytes'] = size1
info1['sha256'] = sha1
results['URL_Phish_V2'] = info1

# =====================================================================
# 2. LegitPhish_V2 — url_features_extracted1.csv
# =====================================================================
print("\n" + "=" * 60)
print("DATASET 2: LegitPhish_V2")
print("=" * 60)

path2 = f'{BASE}/LegitPhish_V2/url_features_extracted1.csv'
size2 = os.path.getsize(path2)
sha2 = sha256_file(path2)
print(f"File: {path2}")
print(f"Size: {size2:,} bytes ({size2/1024/1024:.2f} MB)")
print(f"SHA256: {sha2}")

df2 = pd.read_csv(path2, low_memory=False)
print(f"\nShape: {df2.shape}")
print(f"\nColumns:")
for c in df2.columns:
    print(f"  {c!r:40s} dtype={df2[c].dtype}")

print(f"\nFirst 3 rows:")
print(df2.head(3).to_string())

print(f"\nLast 3 rows:")
print(df2.tail(3).to_string())

url_col2 = None
label_col2 = None
for c in df2.columns:
    cl = c.lower()
    if 'url' in cl and url_col2 is None:
        url_col2 = c
    if cl in ('label', 'class', 'phishing', 'is_phishing', 'target', 'status', 'type'):
        label_col2 = c

print(f"\nIdentified URL column: {url_col2}")
print(f"Identified Label column: {label_col2}")

if label_col2:
    print(f"\nClass distribution for '{label_col2}':")
    vc2 = df2[label_col2].value_counts()
    print(vc2)

print(f"\nMissing values:")
mv2 = df2.isnull().sum()
print(mv2[mv2 > 0] if mv2.sum() > 0 else "  None")

print(f"\nDuplicate rows: {df2.duplicated().sum()}")
if url_col2:
    print(f"Duplicate URLs: {df2[url_col2].duplicated().sum()}")

info2 = inspect_df(df2, url_col2, label_col2)
info2['file'] = 'url_features_extracted1.csv'
info2['size_bytes'] = size2
info2['sha256'] = sha2
results['LegitPhish_V2'] = info2

# =====================================================================
# 3. CompPhish_V4 — All_Features_threshold90.xlsx
# =====================================================================
print("\n" + "=" * 60)
print("DATASET 3: CompPhish_V4")
print("=" * 60)

path3 = f'{BASE}/CompPhish_V4/All_Features_threshold90.xlsx'
size3 = os.path.getsize(path3)
sha3 = sha256_file(path3)
print(f"File: {path3}")
print(f"Size: {size3:,} bytes ({size3/1024/1024:.2f} MB)")
print(f"SHA256: {sha3}")

# Read all sheets
xl = pd.ExcelFile(path3)
print(f"\nSheets: {xl.sheet_names}")

for sheet in xl.sheet_names:
    print(f"\n--- Sheet: '{sheet}' ---")
    df3 = xl.parse(sheet)
    print(f"Shape: {df3.shape}")
    print(f"Columns:")
    for c in df3.columns:
        print(f"  {str(c)!r:40s} dtype={df3[c].dtype}")
    print(f"First 3 rows:")
    print(df3.head(3).to_string())

# Use first/main sheet
df3 = xl.parse(xl.sheet_names[0])

url_col3 = None
label_col3 = None
for c in df3.columns:
    cl = str(c).lower()
    if 'url' in cl and url_col3 is None:
        url_col3 = c
    if cl in ('label', 'class', 'phishing', 'is_phishing', 'target', 'status', 'type', 'result'):
        label_col3 = c

print(f"\nIdentified URL column: {url_col3}")
print(f"Identified Label column: {label_col3}")

if label_col3:
    print(f"\nClass distribution for '{label_col3}':")
    vc3 = df3[label_col3].value_counts()
    print(vc3)

print(f"\nMissing values:")
mv3 = df3.isnull().sum()
print(mv3[mv3 > 0] if mv3.sum() > 0 else "  None")

print(f"\nDuplicate rows: {df3.duplicated().sum()}")

info3 = inspect_df(df3, url_col3, label_col3)
info3['file'] = 'All_Features_threshold90.xlsx'
info3['size_bytes'] = size3
info3['sha256'] = sha3
info3['sheets'] = xl.sheet_names
results['CompPhish_V4'] = info3

# Also inspect Mapping_File.xlsx
path3m = f'{BASE}/CompPhish_V4/Mapping_File.xlsx'
xlm = pd.ExcelFile(path3m)
print(f"\n--- Mapping_File.xlsx sheets: {xlm.sheet_names} ---")
for sheet in xlm.sheet_names:
    dfm = xlm.parse(sheet)
    print(f"Sheet '{sheet}': {dfm.shape}")
    print(dfm.head(5).to_string())
    print()

# Save inspection results
out_path = 'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/metadata/inspection_results.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nInspection results saved to: {out_path}")
