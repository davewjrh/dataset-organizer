import sys, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from organizer import Organizer

external_dataset_dir = r"C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset"
org = Organizer()
try:
    scanned = org.scan_dataset(external_dataset_dir)
    if not scanned:
        print('No devices found or scan returned None')
    else:
        print(f'Found {len(scanned)} device entries')
        for k, samples in list(scanned.items())[:30]:
            sf = samples[0].get('_source_file') if samples and isinstance(samples[0], dict) else None
            print(f' - {k} (sample: {sf})')
    print('Loaded files count:', len(getattr(org, '_loaded_files', [])))
    print('Device file index size:', len(getattr(org, '_device_file_index', {})))
except Exception as e:
    print('Exception during scan:')
    traceback.print_exc()
