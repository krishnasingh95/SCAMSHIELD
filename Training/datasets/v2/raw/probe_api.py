import urllib.request
import urllib.error
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Accept': 'application/json',
}

# Mendeley Data uses a public API - try different known patterns
dataset_ids = [
    ('URL_Phish_V2', '65z9twcx3r', 2),
    ('LegitPhish_V2', 'hx4m73v2sf', 2),
    ('CompPhish_V4', 'fmbs4kp9wz', 4),
]

api_patterns = [
    'https://data.mendeley.com/api/datasets/{id}?version={ver}',
    'https://data.mendeley.com/api/datasets/{id}/files?version={ver}',
    'https://data.mendeley.com/api/datasets-v2/{id}?version={ver}',
    'https://api.mendeley.com/datasets/{id}',
]

for name, did, ver in dataset_ids:
    print(f'=== {name} (ID: {did}, Version: {ver}) ===')
    for pattern in api_patterns:
        url = pattern.format(id=did, ver=ver)
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=20)
            data_raw = resp.read().decode('utf-8', errors='replace')
            print(f'  URL: {url}')
            print(f'  Status: {resp.status}')
            try:
                data = json.loads(data_raw)
                print(f'  JSON keys: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}')
                # Check if it's the right dataset
                if isinstance(data, dict):
                    name_field = data.get('name', data.get('title', ''))
                    print(f'  Name: {name_field}')
                print(f'  Content: {data_raw[:400]}')
            except:
                print(f'  Raw: {data_raw[:400]}')
        except urllib.error.HTTPError as e:
            print(f'  URL: {url} -> HTTP {e.code}: {e.reason}')
        except Exception as e:
            print(f'  URL: {url} -> {type(e).__name__}: {e}')
    print()
