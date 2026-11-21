import urllib.request
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

urls = [
    ('URL_Phish_V2', 'https://data.mendeley.com/datasets/65z9twcx3r/2'),
    ('LegitPhish_V2', 'https://data.mendeley.com/datasets/hx4m73v2sf/2'),
    ('CompPhish_V4', 'https://data.mendeley.com/datasets/fmbs4kp9wz/4'),
]

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=30)
        content = resp.read().decode('utf-8', errors='replace')
        print(f'=== {name} ===')
        print(f'Status: {resp.status}')
        ct = resp.headers.get('Content-Type', 'unknown')
        print(f'Content-Type: {ct}')
        if '<title>' in content:
            start = content.find('<title>') + 7
            end = content.find('</title>', start)
            print(f'Page title: {content[start:end]}')
        print(f'First 300 chars: {content[:300]}')
        print()
    except Exception as e:
        print(f'{name}: {type(e).__name__}: {e}')
        print()
