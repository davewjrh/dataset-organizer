import sys
sys.path.insert(0, 'src')
from organizer import Organizer

ext_dir = r'C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset'
print('Loading external dataset (may take a few seconds)...')
o = Organizer()
_df = o.load_all_from_dir(ext_dir)
if _df is None:
    print('No files found in external dir')
    sys.exit(1)
o.clean_data()
organized = o.organize_by_device()
keys = list(organized.keys())
print('Found', len(keys), 'devices; sample keys:')
print(keys[:20])

from devices import devices as DEVICE_LIST

from pathlib import Path

def compute_label_for_key(k):
    # Look up records
    records = organized.get(k)
    if not records:
        ks = [kk for kk in organized.keys() if str(kk) == str(k)]
        if ks:
            records = organized.get(ks[0])

    # Try folder-derived name from _source_file
    if records and len(records) > 0:
        first = records[0]
        try:
            sf = first.get('_source_file') if isinstance(first, dict) else None
            if sf:
                p = Path(sf)
                parent = p.parent.name
                if parent and parent.lower() not in {'data', 'raw', 'processed', 'dataset'}:
                    return f"{parent} ({k})"
        except Exception:
            pass

        # Preferred payload fields
        preferred = ['deviceInfo.deviceName', 'deviceInfo.name', 'device_name', 'device_label', 'node_name', 'deviceName', 'name']
        blacklist = {'chirpstack', 'the things network', 'ttn', 'lorawan', 'lora', 'network server'}
        for nf in preferred:
            if isinstance(first, dict) and nf in first and first.get(nf):
                val = str(first.get(nf)).strip()
                if val and val.lower() not in blacklist:
                    return f"{val} ({k})"

        # any name-like key
        if isinstance(first, dict):
            for kf, v in first.items():
                lk = kf.lower()
                if ('name' in lk or lk.endswith('_name')) and v:
                    val = str(v).strip()
                    if val and val.lower() not in blacklist:
                        return f"{val} ({k})"

        # match known devices by type string in values
        for dev in DEVICE_LIST:
            try:
                dname = dev.name.lower()
                for v in first.values():
                    try:
                        if dname in str(v).lower():
                            return f"{dev.name} ({k})"
                    except Exception:
                        continue
            except Exception:
                continue

    # fallback to raw key
    return str(k)

labels = [compute_label_for_key(k) for k in keys[:50]]
print('\nSample labels:')
for lbl in labels[:50]:
    print(' -', lbl)
