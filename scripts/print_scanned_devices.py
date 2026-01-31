import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
src_dir = ROOT / 'src'
sys.path.insert(0, str(src_dir))
from organizer import Organizer

external_dataset_dir = r"C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset"
org = Organizer()
scanned = org.scan_dataset(external_dataset_dir)
if not scanned:
    print('No devices found')
    sys.exit(0)

print(f'Found {len(scanned)} device entries:')
for k, samples in scanned.items():
    sf = samples[0].get('_source_file') if samples and isinstance(samples[0], dict) else None
    print(f' - {k} (sample file: {sf})')
