import os
import sys
import json
import csv
from pathlib import Path

ext_dir = r'C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset'

print('Scanning top-level subfolders of:', ext_dir)
if not os.path.exists(ext_dir):
    print('External dataset path does not exist:', ext_dir)
    sys.exit(1)

subdirs = [d for d in Path(ext_dir).iterdir() if d.is_dir()]
print('Found', len(subdirs), 'subfolders; sampling each for a representative device key...')

patterns = ['dev_eui', 'deveui', 'devaddr', 'dev_addr', 'device_id', 'deviceid', 'dev', 'eui']

results = []
for d in subdirs[:200]:  # limit to 200 for speed
    sample_key = None
    sample_file = None
    for ext in ('*.json','*.ndjson','*.jsonl','*.csv'):
        for p in d.rglob(ext):
            sample_file = p
            break
        if sample_file:
            break
    if not sample_file:
        # try files directly under d
        files = list(d.iterdir())
        if files:
            sample_file = files[0]
    if sample_file:
        try:
            if sample_file.suffix.lower() == '.csv':
                with open(sample_file, 'r', encoding='utf-8') as fh:
                    reader = csv.reader(fh)
                    headers = next(reader, [])
                    headers_l = [h.strip().lower() for h in headers]
                    for ptn in patterns:
                        for h,v in zip(headers_l, headers):
                            if ptn in h:
                                # read first data row to extract value
                                row = next(reader, None)
                                if row and len(row) > headers_l.index(h):
                                    sample_key = row[headers_l.index(h)]
                                    break
                        if sample_key:
                            break
            else:
                # JSON/NDJSON: try to load first record only
                if sample_file.suffix.lower() in ('.ndjson', '.jsonl'):
                    with open(sample_file, 'r', encoding='utf-8') as fh:
                        line = fh.readline()
                        obj = json.loads(line) if line else None
                else:
                    with open(sample_file, 'r', encoding='utf-8') as fh:
                        obj = json.load(fh)
                        if isinstance(obj, list) and obj:
                            obj = obj[0]
                if isinstance(obj, dict):
                    # look for direct keys
                    for k,v in obj.items():
                        lk = k.lower()
                        for ptn in patterns:
                            if ptn in lk and v:
                                sample_key = v
                                break
                        if sample_key:
                            break
                    # try nested keys by searching str(obj)
                    if not sample_key:
                        s = json.dumps(obj)
                        for ptn in patterns:
                            if ptn in s.lower():
                                # best-effort: extract nearby value via simple parsing
                                sample_key = '(found-'+ptn+')'
                                break
        except Exception:
            pass
    folder = d.name
    results.append((folder, str(sample_key) if sample_key is not None else None, str(sample_file) if sample_file else None))

# print results
for folder, key, fpath in results:
    print(f"{folder} ({key}) - sample file: {fpath}")

print('\nDone. If folder names look correct, the GUI will now prefer these folder names as device labels.')
