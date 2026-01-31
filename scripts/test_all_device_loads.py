import sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from organizer import Organizer
external_dataset_dir = r"C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset"
org = Organizer()
scanned = org.scan_dataset(external_dataset_dir)
print('Found', len(scanned) if scanned else 0, 'folders')
if not scanned:
    sys.exit(0)

results = []
for k in scanned.keys():
    t0 = time.time()
    recs = org.load_device_full(k)
    dt = time.time() - t0
    n = len(recs) if recs else 0
    results.append((k, n, dt))
    print(f'{k}: {n} records in {dt:.2f}s')

print('\nSummary:')
for k, n, dt in results:
    print(f'{k}: {n} records, {dt:.2f}s')
