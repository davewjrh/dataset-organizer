import sys
sys.path.insert(0, r'c:\Users\davew\OneDrive - Carleton University\Workspace\dataset-organizer\src')
from organizer import Organizer
from pprint import pprint

org = Organizer()
sc = org.scan_dataset(r'c:\Users\davew\OneDrive - Carleton University\Workspace\dataset-organizer\data\raw', sample_per_device=1, max_files=200)
if not sc:
    print('no devices found')
    raise SystemExit(0)
key = list(sc.keys())[0]
print('device key:', key)
full = org.load_device_full(key)
print('loaded', len(full), 'records')
for i, r in enumerate(full[:5]):
    print('\nrecord', i)
    pprint(list(r.items())[:20])
    rx = r.get('rxinfo')
    print('rxinfo type:', type(rx))
    try:
        print('rxinfo repr snippet:', repr(rx)[:400])
    except Exception:
        pass

print('\ndone')
