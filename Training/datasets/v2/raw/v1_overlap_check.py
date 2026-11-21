"""Quick V1 vs V2 overlap check"""
import pandas as pd, json

BASE = 'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/external'

df1 = pd.read_csv(f'{BASE}/URL_Phish_V2/Dataset.csv', usecols=['url'], low_memory=False)
df2 = pd.read_csv(f'{BASE}/LegitPhish_V2/url_features_extracted1.csv', usecols=['URL'], low_memory=False)
df2 = df2.rename(columns={'URL': 'url'})
df3m = pd.read_excel(f'{BASE}/CompPhish_V4/Mapping_File.xlsx', usecols=['url'])
df_v1 = pd.read_csv('C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/raw/PhiUSIIL_Phishing_URL_Dataset.csv', usecols=['URL'], low_memory=False)

urls1 = set(df1['url'].dropna().str.strip())
urls2 = set(df2['url'].dropna().str.strip())
urls3 = set(df3m['url'].dropna().str.strip())
urls_v1 = set(df_v1['URL'].dropna().str.strip())

print("V1 PhiUSIIL URLs:", len(urls_v1))
print("V1 AND URL_Phish_V2:", len(urls_v1 & urls1))
print("V1 AND LegitPhish_V2:", len(urls_v1 & urls2))
print("V1 AND CompPhish_V4:", len(urls_v1 & urls3))

# Update the saved json with v1 overlap info
with open('C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/metadata/url_overlap_summary.json') as f:
    data = json.load(f)

data['V1_PhiUSIIL_unique_urls'] = len(urls_v1)
data['overlap_V1_and_URL_Phish_V2'] = len(urls_v1 & urls1)
data['overlap_V1_and_LegitPhish_V2'] = len(urls_v1 & urls2)
data['overlap_V1_and_CompPhish_V4'] = len(urls_v1 & urls3)

with open('C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/metadata/url_overlap_summary.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Done. Saved updated overlap summary.")
