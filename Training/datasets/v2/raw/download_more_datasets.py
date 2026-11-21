"""
Download additional Mendeley phishing datasets for ScamShield V2 expanded training.
Datasets:
1. 3jddhy2f6s: Phishing URL dataset (Tandin Wangchuk) - DOI: 10.17632/3jddhy2f6s.1
2. c2gw7fy2j4: Web page phishing detection (Hannousse & Yahiouche) - DOI: 10.17632/c2gw7fy2j4.3
3. 5fk24y4xmg: MURL Large-Scale Malicious URL Dataset (Ibnath et al.) - DOI: 10.17632/5fk24y4xmg.2
"""

import os
import sys
import hashlib
import urllib.request

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = r"C:\Users\x1605\AI_Projects\ScamShield"
ARCHIVES = os.path.join(ROOT, r"Training\datasets\V2\raw\archives")
EXT_BASE = os.path.join(ROOT, r"Training\datasets\V2\raw\external")

DATASETS = [
    {
        "id": "3jddhy2f6s",
        "name": "Phishing_URL_3jddhy2f6s",
        "file": "dataset2.csv",
        "url": "https://data.mendeley.com/public-files/datasets/3jddhy2f6s/files/575f34ca-98c8-42cd-affe-7dad6aaf17a2/file_downloaded",
        "sha256": "fccce1a99282b5df019316d3f251d14cf3673c683b5d259c8443905e94b293e5"
    },
    {
        "id": "c2gw7fy2j4",
        "name": "WebPage_Phishing_c2gw7fy2j4",
        "file": "dataset_B_05_2020.csv",
        "url": "https://data.mendeley.com/public-files/datasets/c2gw7fy2j4/files/575316f4-ee1d-453e-a04f-7b950915b61b/file_downloaded",
        "sha256": "21093e2902e52b2bc3fba4313fa7d1217fc38e553feebc11c5f3e913a89e40ef"
    },
    {
        "id": "5fk24y4xmg",
        "name": "MURL_5fk24y4xmg",
        "file": "Malicious_URL_Detection.csv",
        "url": "https://data.mendeley.com/public-files/datasets/5fk24y4xmg/files/3d95c20f-afdf-46d3-b85b-bdf049ca57fd/file_downloaded",
        "sha256": "3d95c20f" # prefix check or compute
    }
]

headers = {'User-Agent': 'Mozilla/5.0'}

for ds in DATASETS:
    target_dir = os.path.join(EXT_BASE, ds["name"])
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, ds["file"])
    archive_path = os.path.join(ARCHIVES, f"{ds['id']}_{ds['file']}")

    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        print(f"[{ds['id']}] Already downloaded: {target_path} ({os.path.getsize(target_path):,} bytes)")
        continue

    print(f"\nDownloading {ds['id']} ({ds['file']})...")
    req = urllib.request.Request(ds["url"], headers=headers)
    
    with urllib.request.urlopen(req, timeout=120) as resp, open(target_path, "wb") as f_out:
        total_len = int(resp.headers.get('Content-Length', 0))
        downloaded = 0
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            f_out.write(chunk)
            downloaded += len(chunk)
            if total_len > 0:
                pct = downloaded * 100 // total_len
                print(f"\r  {downloaded:,}/{total_len:,} bytes ({pct}%)", end="", flush=True)

    print()
    # Compute SHA256
    h = hashlib.sha256()
    with open(target_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    actual_sha = h.hexdigest()
    print(f"  Downloaded: {os.path.getsize(target_path):,} bytes | SHA256: {actual_sha}")

    # Copy to archives
    import shutil
    shutil.copy2(target_path, archive_path)
    print(f"  Archived to: {archive_path}")

print("\nAll downloads completed successfully!")
