# Diagnostic script: inspect_device_samples.py
# Scans data/raw (limited) and prints samples, collected keys, and sample values.
import sys
sys.path.insert(0, r'c:\Users\davew\OneDrive - Carleton University\Workspace\dataset-organizer\src')
from organizer import Organizer
from pathlib import Path
import pprint

BASE = Path(r"c:\Users\davew\OneDrive - Carleton University\Workspace\dataset-organizer\data\raw")
print('Scanning', BASE)
o = Organizer()
# limit files to avoid long runs
d = o.scan_dataset(str(BASE), sample_per_device=3, max_files=200)
if not d:
    print('No devices found')
    raise SystemExit(0)

print('Found devices:', len(d))

# helper functions (same logic as GUI)

def collect_keys(rec, prefix=''):
    keys = set()
    if isinstance(rec, dict):
        for kk, vv in rec.items():
            if kk.startswith('_'):
                continue
            new_key = f"{prefix}.{kk}" if prefix else kk
            if isinstance(vv, dict):
                keys.update(collect_keys(vv, new_key))
            else:
                keys.add(new_key)
    return keys


def get_nested(rec, key):
    if not isinstance(rec, dict):
        return None
    if key in rec:
        return rec.get(key)
    if '.' in key:
        cur = rec
        for part in key.split('.'):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur
    alt = key.replace('.', '_')
    if alt in rec:
        return rec.get(alt)
    # case-insensitive top-level
    lk = key.lower()
    for kf, v in rec.items():
        if isinstance(kf, str) and kf.lower() == lk:
            return v
    return None


# Inspect up to 5 devices
for i, k in enumerate(list(d.keys())[:5]):
    print('\n=== Device', i+1, 'key=', k)
    recs = d.get(k, [])
    print('Sample records count:', len(recs))
    pprint.pprint(recs[:3])
    if recs:
        keys = collect_keys(recs[0])
        print('\nCollected keys (sample):')
        for kk in sorted(keys)[:50]:
            print(' -', kk)
        print('\nSample values for keys:')
        for kk in sorted(keys)[:20]:
            vals = [get_nested(r, kk) for r in recs[:3]]
            print(f" {kk} -> {vals}")
    # If scan built index, try full load
    if hasattr(o, '_device_file_index') and k in getattr(o, '_device_file_index', {}):
        full = o.load_device_full(k)
        print('\nFull load returned', len(full), 'records; sample keys:')
        if full:
            print(list(full[0].keys())[:50])

print('\nDone')
