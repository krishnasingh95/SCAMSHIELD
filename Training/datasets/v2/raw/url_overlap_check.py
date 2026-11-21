"""
ScamShield V2 — URL Overlap Analysis
Checks for URL overlap between the three external datasets.
"""
import pandas as pd
import json

BASE = 'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/external'

# Load all three URL sets
print("Loading URL_Phish_V2...")
df1 = pd.read_csv(f'{BASE}/URL_Phish_V2/Dataset.csv', usecols=['url', 'label'], low_memory=False)

print("Loading LegitPhish_V2...")
df2 = pd.read_csv(f'{BASE}/LegitPhish_V2/url_features_extracted1.csv', usecols=['URL', 'ClassLabel'], low_memory=False)
df2 = df2.rename(columns={'URL': 'url', 'ClassLabel': 'label'})

print("Loading CompPhish_V4 Mapping...")
df3m = pd.read_excel(f'{BASE}/CompPhish_V4/Mapping_File.xlsx', usecols=['url', 'label'])

urls1 = set(df1['url'].dropna().str.strip())
urls2 = set(df2['url'].dropna().str.strip())
urls3 = set(df3m['url'].dropna().str.strip())

print(f"\nURL counts:")
print(f"  URL_Phish_V2:  {len(urls1):,}")
print(f"  LegitPhish_V2: {len(urls2):,}")
print(f"  CompPhish_V4:  {len(urls3):,}")

print(f"\n--- Cross-dataset overlaps ---")
o12 = urls1 & urls2
o13 = urls1 & urls3
o23 = urls2 & urls3
o123 = urls1 & urls2 & urls3
all_urls = urls1 | urls2 | urls3

print(f"URL_Phish_V2 AND LegitPhish_V2: {len(o12):,}")
print(f"URL_Phish_V2 AND CompPhish_V4:  {len(o13):,}")
print(f"LegitPhish_V2 AND CompPhish_V4: {len(o23):,}")
print(f"All three:                       {len(o123):,}")
print(f"Union (total unique URLs):       {len(all_urls):,}")

# Also check vs V1 PhiUSIIL dataset
print("\nLoading V1 PhiUSIIL dataset...")
try:
    df_v1 = pd.read_csv('C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/raw/PhiUSIIL_Phishing_URL_Dataset.csv', 
                         usecols=['URL'], low_memory=False)
    urls_v1 = set(df_v1['URL'].dropna().str.strip())
    print(f"V1 PhiUSIIL URLs: {len(urls_v1):,}")
    o_v1_1 = urls_v1 & urls1
    o_v1_2 = urls_v1 & urls2
    o_v1_3 = urls_v1 & urls3
    print(f"V1 ∩ URL_Phish_V2:  {len(o_v1_1):,}")
    print(f"V1 ∩ LegitPhish_V2: {len(o_v1_2):,}")
    print(f"V1 ∩ CompPhish_V4:  {len(o_v1_3):,}")
except Exception as e:
    print(f"Could not load V1 data: {e}")

overlap_summary = {
    "URL_Phish_V2_unique_urls": len(urls1),
    "LegitPhish_V2_unique_urls": len(urls2),
    "CompPhish_V4_unique_urls": len(urls3),
    "overlap_phish_legit": len(o12),
    "overlap_phish_comp": len(o13),
    "overlap_legit_comp": len(o23),
    "overlap_all_three": len(o123),
    "total_unique_across_all": len(all_urls),
}

out = 'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/metadata/url_overlap_summary.json'
with open(out, 'w') as f:
    json.dump(overlap_summary, f, indent=2)
print(f"\nSaved overlap summary to: {out}")
