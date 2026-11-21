import urllib.request
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Accept': 'application/json',
}

datasets = [
    ('URL_Phish_V2', '65z9twcx3r', 2),
    ('LegitPhish_V2', 'hx4m73v2sf', 2),
    ('CompPhish_V4', 'fmbs4kp9wz', 4),
]

all_info = {}

for name, did, ver in datasets:
    url = f'https://data.mendeley.com/api/datasets/{did}/files?version={ver}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=30)
    files = json.loads(resp.read().decode('utf-8'))
    
    print(f'=== {name} ===')
    dataset_files = []
    for f in files:
        filename = f.get('filename', 'unknown')
        file_id = f.get('id', '')
        content = f.get('content_details', {})
        size = content.get('size', 0)
        sha256 = content.get('sha256_hash', '')
        download_url = content.get('download_url', '')
        content_type = content.get('content_type', '')
        
        print(f'  File: {filename}')
        print(f'    ID: {file_id}')
        print(f'    Size: {size:,} bytes ({size/1024/1024:.2f} MB)')
        print(f'    SHA256: {sha256}')
        print(f'    Content-Type: {content_type}')
        print(f'    Download URL: {download_url}')
        print()
        
        dataset_files.append({
            'filename': filename,
            'file_id': file_id,
            'size_bytes': size,
            'sha256': sha256,
            'content_type': content_type,
            'download_url': download_url,
        })
    
    all_info[name] = dataset_files

# Save to JSON for reference
with open('C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/mendeley_file_list.json', 'w') as f:
    json.dump(all_info, f, indent=2)

print("Saved to mendeley_file_list.json")
