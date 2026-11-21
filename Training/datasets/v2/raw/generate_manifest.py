"""
Generate dataset_manifest.json and dataset_download_audit.csv for ScamShield V2
"""
import json
import csv
from datetime import datetime, timezone
import os

METADATA_DIR = 'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/metadata'
BASE_EXT = 'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/external'
ARCHIVES_DIR = 'C:/Users/x1605/AI_Projects/ScamShield/Training/datasets/V2/raw/archives'

retrieval_date = "2026-11-13T04:11:00Z"  # UTC time of download (approx)

manifest = {
    "schema_version": "1.0",
    "project": "ScamShield V2",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "note": "Original downloaded files must NOT be modified. Label normalization will occur only in processed copies.",
    "scamshield_label_convention": {
        "SAFE": 0,
        "PHISHING": 1
    },
    "datasets": [
        {
            "dataset_name": "URL-Phish",
            "internal_id": "URL_Phish_V2",
            "version": 2,
            "doi": "10.17632/65z9twcx3r.2",
            "repository": "Mendeley Data",
            "mendeley_dataset_id": "65z9twcx3r",
            "url": "https://data.mendeley.com/datasets/65z9twcx3r/2",
            "license": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "retrieval_date_utc": retrieval_date,
            "original_archive_filename": "URL_Phish_V2_Dataset.csv",
            "archive_location": f"{ARCHIVES_DIR}/URL_Phish_V2_Dataset.csv",
            "extracted_files": [
                {
                    "filename": "Dataset.csv",
                    "location": f"{BASE_EXT}/URL_Phish_V2/Dataset.csv",
                    "size_bytes": 15149338,
                    "size_mb": 14.45,
                    "sha256": "d68b3cd0648dcf9c775347416ad1a8995e8a025921fbe3871ca6158d4db3c3a1",
                    "file_type": "text/csv"
                }
            ],
            "record_count": 116600,
            "column_count": 26,
            "url_column": "url",
            "label_column": "label",
            "original_label_mapping": {
                "0": "Benign",
                "1": "Phishing"
            },
            "scamshield_label_mapping_note": "0=Benign -> ScamShield SAFE(0); 1=Phishing -> ScamShield PHISHING(1). No label inversion needed.",
            "class_distribution": {
                "0_Benign": 100000,
                "1_Phishing": 16600
            },
            "class_ratio_phishing_pct": 14.24,
            "missing_values": {"tld": 14},
            "total_missing_values": 14,
            "duplicate_rows": 1369,
            "unique_urls": 115231,
            "duplicate_urls": 1369,
            "has_pre_extracted_features": True,
            "feature_columns": [
                "url_len", "dom", "dom_len", "is_ip", "tld", "tld_len", "subdom_cnt",
                "letter_cnt", "digit_cnt", "special_cnt", "eq_cnt", "qm_cnt", "amp_cnt",
                "dot_cnt", "dash_cnt", "under_cnt", "letter_ratio", "digit_ratio",
                "spec_ratio", "is_https", "slash_cnt", "entropy", "path_len", "query_len"
            ],
            "verified_download": True,
            "sha256_verified": True
        },
        {
            "dataset_name": "LegitPhish Dataset",
            "internal_id": "LegitPhish_V2",
            "version": 2,
            "doi": "10.17632/hx4m73v2sf.2",
            "repository": "Mendeley Data",
            "mendeley_dataset_id": "hx4m73v2sf",
            "url": "https://data.mendeley.com/datasets/hx4m73v2sf/2",
            "license": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "retrieval_date_utc": retrieval_date,
            "original_archive_filename": "LegitPhish_V2_url_features_extracted1.csv",
            "archive_location": f"{ARCHIVES_DIR}/LegitPhish_V2_url_features_extracted1.csv",
            "extracted_files": [
                {
                    "filename": "url_features_extracted1.csv",
                    "location": f"{BASE_EXT}/LegitPhish_V2/url_features_extracted1.csv",
                    "size_bytes": 8963838,
                    "size_mb": 8.55,
                    "sha256": "8685e7901c3b4e73eb43c106cb166cc932dd14f76960a032c713c2c32f09dbcd",
                    "file_type": "text/csv"
                }
            ],
            "record_count": 101219,
            "column_count": 18,
            "url_column": "URL",
            "label_column": "ClassLabel",
            "original_label_mapping": {
                "0.0": "Phishing",
                "1.0": "Legitimate"
            },
            "scamshield_label_mapping_note": "INVERTED: 0=Phishing -> ScamShield PHISHING(1); 1=Legitimate -> ScamShield SAFE(0). Label inversion REQUIRED during preprocessing.",
            "class_distribution_note": "ClassLabel has 1 missing value. Full distribution requires further analysis after dropping nulls.",
            "missing_values": {"ClassLabel": 1},
            "total_missing_values": 1,
            "duplicate_rows": 346,
            "unique_urls": 100873,
            "duplicate_urls": 346,
            "has_pre_extracted_features": True,
            "feature_columns": [
                "url_length", "has_ip_address", "dot_count", "https_flag", "url_entropy",
                "token_count", "subdomain_count", "query_param_count", "tld_length",
                "path_length", "has_hyphen_in_domain", "number_of_digits", "tld_popularity",
                "suspicious_file_extension", "domain_name_length", "percentage_numeric_chars"
            ],
            "verified_download": True,
            "sha256_verified": True,
            "WARNING": "Significant overlap with V1 PhiUSIIL dataset: 36,936 shared URLs detected. Must deduplicate before combining with V1 data."
        },
        {
            "dataset_name": "CompPhish",
            "internal_id": "CompPhish_V4",
            "version": 4,
            "doi": "10.17632/fmbs4kp9wz.4",
            "repository": "Mendeley Data",
            "mendeley_dataset_id": "fmbs4kp9wz",
            "url": "https://data.mendeley.com/datasets/fmbs4kp9wz/4",
            "license": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "retrieval_date_utc": retrieval_date,
            "original_archive_filenames": [
                "CompPhish_V4_All_Features_threshold90.xlsx",
                "CompPhish_V4_Data_Dictionary.xlsx",
                "CompPhish_V4_Mapping_File.xlsx",
                "CompPhish_V4_Readme.docx"
            ],
            "skipped_files": [
                {
                    "filename": "All_HTML.zip",
                    "size_bytes": 725995327,
                    "reason": "Data security: HTML files must not be opened/rendered. Not required for ML training. Skipped per data security policy.",
                    "sha256": "12440e4f911fabf4ec2c712ae014cb43e638e9a6adc6c7c6a506a8a7df24fcf7"
                },
                {
                    "filename": "dataset Creator.zip",
                    "size_bytes": 9710,
                    "reason": "Data security: executable/script archive. Not inspected.",
                    "sha256": "0462b4c4d8e1b4b68eb516c1657ec6d3646ec8dab81e1a2f2dc08eb5a13b3fa2"
                },
                {
                    "filename": "feature extractor.zip",
                    "size_bytes": 34276,
                    "reason": "Data security: executable/script archive. Not inspected.",
                    "sha256": "0e72f280a189fdc91c65aa3035334676df26018da8d5b751a0d3f980007b858a"
                },
                {
                    "filename": "requirements.txt",
                    "size_bytes": 166,
                    "reason": "Dataset creator tool dependency — not training data.",
                    "sha256": "d8c1469acf0841ef38323e0050abe6757b376e919bc3a1b8bb13155c13d12eef"
                }
            ],
            "extracted_files": [
                {
                    "filename": "All_Features_threshold90.xlsx",
                    "location": f"{BASE_EXT}/CompPhish_V4/All_Features_threshold90.xlsx",
                    "size_bytes": 4726765,
                    "size_mb": 4.51,
                    "sha256": "6e87b7997c2d0e9e3f1e02fd5ee1240442385f9bea5f0a40e46e7b6e43ada21b",
                    "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "sheets": ["Sheet1"],
                    "rows": 15358,
                    "columns": 73,
                    "note": "Full feature dataset including HTML-based features (73 columns)"
                },
                {
                    "filename": "Data_Dictionary.xlsx",
                    "location": f"{BASE_EXT}/CompPhish_V4/Data_Dictionary.xlsx",
                    "size_bytes": 18182,
                    "size_mb": 0.02,
                    "sha256": "a4237dd99d7f4a55edc3ffe88a416db77b1734f7c5d52677f8f0c86bf8b88470",
                    "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "note": "Feature definitions and descriptions"
                },
                {
                    "filename": "Mapping_File.xlsx",
                    "location": f"{BASE_EXT}/CompPhish_V4/Mapping_File.xlsx",
                    "size_bytes": 635936,
                    "size_mb": 0.61,
                    "sha256": "e6dda6a21d925f8aba36090f295b08e9808a5dfe8dd3276bf8cd82022855f14a",
                    "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "note": "URL-to-label mapping (serial_number, url, label). 15,358 rows, 3 columns.",
                    "columns": ["serial_number", "url", "label"]
                },
                {
                    "filename": "Readme.docx",
                    "location": f"{BASE_EXT}/CompPhish_V4/Readme.docx",
                    "size_bytes": 18710,
                    "size_mb": 0.02,
                    "sha256": "b6bb0dcec059a5fa0e01a380c711ea5d27d2577727f3d407a0012276a72b9083",
                    "file_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "note": "Dataset documentation"
                }
            ],
            "primary_data_file": "All_Features_threshold90.xlsx",
            "url_mapping_file": "Mapping_File.xlsx",
            "record_count": 15358,
            "column_count": 73,
            "url_column": "url",
            "label_column": "label",
            "original_label_mapping": {
                "0": "Legitimate",
                "1": "Phishing"
            },
            "scamshield_label_mapping_note": "0=Legitimate -> ScamShield SAFE(0); 1=Phishing -> ScamShield PHISHING(1). No label inversion needed.",
            "class_distribution": {
                "0_Legitimate": 8154,
                "1_Phishing": 7204
            },
            "class_ratio_phishing_pct": 46.9,
            "missing_values": {},
            "total_missing_values": 0,
            "duplicate_rows": 0,
            "unique_urls": 15351,
            "duplicate_urls": 0,
            "has_pre_extracted_features": True,
            "includes_html_features": True,
            "feature_columns_note": "73 columns including URL, HTML, and DOM-based features. See Data_Dictionary.xlsx for descriptions.",
            "verified_download": True,
            "sha256_verified": True
        }
    ]
}

manifest_path = f'{METADATA_DIR}/dataset_manifest.json'
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print(f"Saved manifest: {manifest_path}")

# --- Dataset Download Audit CSV ---
audit_rows = []
for ds in manifest['datasets']:
    for ef in ds.get('extracted_files', []):
        audit_rows.append({
            'dataset_name': ds['dataset_name'],
            'internal_id': ds['internal_id'],
            'version': ds['version'],
            'doi': ds['doi'],
            'repository': ds['repository'],
            'license': ds['license'],
            'retrieval_date_utc': ds['retrieval_date_utc'],
            'filename': ef['filename'],
            'location': ef.get('location', ''),
            'size_bytes': ef.get('size_bytes', ''),
            'size_mb': ef.get('size_mb', ''),
            'sha256': ef.get('sha256', ''),
            'sha256_verified': ds.get('sha256_verified', False),
            'download_status': 'SUCCESS',
            'record_count': ds.get('record_count', ''),
            'url_column': ds.get('url_column', ''),
            'label_column': ds.get('label_column', ''),
            'original_label_0': list(ds.get('original_label_mapping', {}).items())[0][1] if ds.get('original_label_mapping') else '',
            'original_label_1': list(ds.get('original_label_mapping', {}).items())[1][1] if len(ds.get('original_label_mapping', {})) > 1 else '',
            'label_inversion_needed': 'YES' if 'INVERTED' in ds.get('scamshield_label_mapping_note', '') else 'NO',
            'duplicate_rows': ds.get('duplicate_rows', ''),
            'missing_values': str(ds.get('missing_values', {})),
        })
    for sf in ds.get('skipped_files', []):
        audit_rows.append({
            'dataset_name': ds['dataset_name'],
            'internal_id': ds['internal_id'],
            'version': ds['version'],
            'doi': ds['doi'],
            'repository': ds['repository'],
            'license': ds['license'],
            'retrieval_date_utc': ds['retrieval_date_utc'],
            'filename': sf['filename'],
            'location': 'SKIPPED',
            'size_bytes': sf.get('size_bytes', ''),
            'size_mb': '',
            'sha256': sf.get('sha256', ''),
            'sha256_verified': 'N/A',
            'download_status': f"SKIPPED: {sf.get('reason', '')}",
            'record_count': '',
            'url_column': '',
            'label_column': '',
            'original_label_0': '',
            'original_label_1': '',
            'label_inversion_needed': 'N/A',
            'duplicate_rows': '',
            'missing_values': '',
        })

audit_path = f'{METADATA_DIR}/dataset_download_audit.csv'
fieldnames = list(audit_rows[0].keys())
with open(audit_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(audit_rows)
print(f"Saved audit CSV: {audit_path}")
print(f"Audit rows: {len(audit_rows)}")
