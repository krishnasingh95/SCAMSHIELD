import urllib.request
import urllib.error
import hashlib
import os
import sys
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Accept': '*/*',
    'Referer': 'https://data.mendeley.com/',
}

DOWNLOAD_PLAN = [
    # (dataset_name, filename, download_url, expected_sha256, dest_dir)
    (
        'URL_Phish_V2',
        'Dataset.csv',
        'https://data.mendeley.com/public-files/datasets/65z9twcx3r/files/0e9c55e4-9adb-43f5-8403-1bbd143ebdb6/file_downloaded',
        'd68b3cd0648dcf9c775347416ad1a8995e8a025921fbe3871ca6158d4db3c3a1',
        'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/external/URL_Phish_V2',
    ),
    (
        'LegitPhish_V2',
        'url_features_extracted1.csv',
        'https://data.mendeley.com/public-files/datasets/hx4m73v2sf/files/0ed51e4d-d160-4047-b650-3f0801eea4aa/file_downloaded',
        '8685e7901c3b4e73eb43c106cb166cc932dd14f76960a032c713c2c32f09dbcd',
        'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/external/LegitPhish_V2',
    ),
    (
        'CompPhish_V4',
        'All_Features_threshold90.xlsx',
        'https://data.mendeley.com/public-files/datasets/fmbs4kp9wz/files/aadc8397-86e9-4d01-a19e-a4144b3a058d/file_downloaded',
        '6e87b7997c2d0e9e3f1e02fd5ee1240442385f9bea5f0a40e46e7b6e43ada21b',
        'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/external/CompPhish_V4',
    ),
    (
        'CompPhish_V4',
        'Data_Dictionary.xlsx',
        'https://data.mendeley.com/public-files/datasets/fmbs4kp9wz/files/fd4547ab-3100-45ca-bd62-171523e8f720/file_downloaded',
        'a4237dd99d7f4a55edc3ffe88a416db77b1734f7c5d52677f8f0c86bf8b88470',
        'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/external/CompPhish_V4',
    ),
    (
        'CompPhish_V4',
        'Mapping_File.xlsx',
        'https://data.mendeley.com/public-files/datasets/fmbs4kp9wz/files/867c433a-8cf3-459e-bb07-54f0f83fea60/file_downloaded',
        'e6dda6a21d925f8aba36090f295b08e9808a5dfe8dd3276bf8cd82022855f14a',
        'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/external/CompPhish_V4',
    ),
    (
        'CompPhish_V4',
        'Readme.docx',
        'https://data.mendeley.com/public-files/datasets/fmbs4kp9wz/files/15a313c5-6ac2-4b02-add0-9ec2a25670cf/file_downloaded',
        'b6bb0dcec059a5fa0e01a380c711ea5d27d2577727f3d407a0012276a72b9083',
        'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/external/CompPhish_V4',
    ),
]

ARCHIVES_DIR = 'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/archives'

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def download_file(url, dest_path, expected_sha256=None, label=''):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    if os.path.exists(dest_path):
        actual = compute_sha256(dest_path)
        if expected_sha256 and actual == expected_sha256:
            print(f'  [SKIP] Already exists and SHA256 matches: {os.path.basename(dest_path)}')
            return True, 'already_exists', actual
        else:
            print(f'  [RE-DL] File exists but SHA256 mismatch — re-downloading: {os.path.basename(dest_path)}')
    
    print(f'  Downloading: {label} -> {os.path.basename(dest_path)}')
    sys.stdout.flush()
    
    req = urllib.request.Request(url, headers=HEADERS)
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            total = int(resp.headers.get('Content-Length', 0))
            downloaded = 0
            with open(dest_path, 'wb') as out:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    out.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded * 100 // total
                        print(f'\r    {downloaded:,}/{total:,} bytes ({pct}%)', end='', flush=True)
            print()
    except urllib.error.HTTPError as e:
        print(f'  ERROR HTTP {e.code}: {e.reason}')
        return False, f'HTTP_{e.code}', None
    except Exception as e:
        print(f'  ERROR: {e}')
        return False, str(e), None
    
    actual_sha256 = compute_sha256(dest_path)
    size = os.path.getsize(dest_path)
    print(f'  Downloaded: {size:,} bytes')
    print(f'  SHA256: {actual_sha256}')
    
    if expected_sha256:
        if actual_sha256 == expected_sha256:
            print(f'  SHA256 VERIFIED OK')
        else:
            print(f'  SHA256 MISMATCH! Expected: {expected_sha256}')
            return False, 'sha256_mismatch', actual_sha256
    
    return True, 'downloaded', actual_sha256

results = {}

for ds_name, filename, dl_url, exp_sha256, dest_dir in DOWNLOAD_PLAN:
    print(f'\n--- {ds_name}: {filename} ---')
    dest_path = os.path.join(dest_dir, filename)
    archive_path = os.path.join(ARCHIVES_DIR, f'{ds_name}_{filename}')
    
    success, status, actual_sha256 = download_file(dl_url, dest_path, exp_sha256, f'{ds_name}/{filename}')
    
    # Also copy to archives
    if success and status == 'downloaded':
        import shutil
        shutil.copy2(dest_path, archive_path)
        print(f'  Copied to archives: {archive_path}')
    
    if ds_name not in results:
        results[ds_name] = []
    results[ds_name].append({
        'filename': filename,
        'dest_path': dest_path,
        'success': success,
        'status': status,
        'sha256': actual_sha256,
        'size': os.path.getsize(dest_path) if success and os.path.exists(dest_path) else 0,
    })

print('\n\n=== DOWNLOAD SUMMARY ===')
for ds_name, files in results.items():
    print(f'\n{ds_name}:')
    for f in files:
        status_str = 'OK' if f['success'] else 'FAILED'
        print(f"  [{status_str}] {f['filename']} ({f['size']:,} bytes) - {f['status']}")
