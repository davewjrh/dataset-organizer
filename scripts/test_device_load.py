import sys
import time
from pathlib import Path

# ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
src_dir = ROOT / 'src'
sys.path.insert(0, str(src_dir))

from organizer import Organizer

external_dataset_dir = r"C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset"

org = Organizer()
print('Scanning dataset...')
start = time.time()
scanned = org.scan_dataset(external_dataset_dir)
scan_time = time.time() - start
print(f'Scan finished in {scan_time:.2f}s; found {len(scanned) if scanned else 0} folders')
if not scanned:
    sys.exit(0)

# pick first key
key = next(iter(scanned.keys()))
print('Sample key:', key)

print('Loading full device data for key:', key)
start = time.time()
records = org.load_device_full(key)
load_time = time.time() - start
print(f'Loaded {len(records)} records in {load_time:.2f}s')

# show a sample record
if records:
    import json
    print('Sample record (first):')
    print(json.dumps(records[0], indent=2)[:2000])
