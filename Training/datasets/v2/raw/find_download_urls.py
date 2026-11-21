import urllib.request
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

datasets = [
    ('URL_Phish_V2', 'https://data.mendeley.com/datasets/65z9twcx3r/2'),
    ('LegitPhish_V2', 'https://data.mendeley.com/datasets/hx4m73v2sf/2'),
    ('CompPhish_V4', 'https://data.mendeley.com/datasets/fmbs4kp9wz/4'),
]

for name, url in datasets:
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=30)
        content = resp.read().decode('utf-8', errors='replace')
        print(f'=== {name} ===')
        
        # Look for JSON-LD or embedded JSON data
        # Find __NEXT_DATA__ or similar embedded state
        if '__NEXT_DATA__' in content:
            start = content.find('__NEXT_DATA__') + 15
            start = content.find('>', start) + 1
            end = content.find('</script>', start)
            json_data = content[start:end]
            try:
                data = json.loads(json_data)
                print(json.dumps(data, indent=2)[:3000])
            except:
                print("Could not parse JSON")
                print(json_data[:1000])
        
        # Also look for download links
        download_links = re.findall(r'href="([^"]*download[^"]*)"', content, re.IGNORECASE)
        print(f'Download links found: {download_links[:10]}')
        
        # Look for file IDs
        file_ids = re.findall(r'"fileId":"([^"]+)"', content)
        print(f'File IDs: {file_ids[:10]}')
        
        # Look for api.mendeley references
        api_refs = re.findall(r'(https?://[^"\']*mendeley[^"\']*)', content)
        print(f'Mendeley API refs: {set(api_refs[:10])}')
        
        print()
    except Exception as e:
        print(f'{name}: {type(e).__name__}: {e}')
        print()
