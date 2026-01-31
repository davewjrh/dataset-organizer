import sys
sys.path.insert(0, r'c:\Users\davew\OneDrive - Carleton University\Workspace\dataset-organizer\src')
from organizer import Organizer
from visualizer import Visualizer

org = Organizer()
sc = org.scan_dataset(r'c:\Users\davew\OneDrive - Carleton University\Workspace\dataset-organizer\data\raw', sample_per_device=1, max_files=200)
print('scanned devices:', list(sc.keys())[:5])
if not sc:
    print('no devices')
    raise SystemExit(0)
key = list(sc.keys())[0]
print('loading full for', key)
full = org.load_device_full(key)
print('loaded records:', len(full))
# try measurements candidates
cands = set()
for r in full[:20]:
    cands.update(r.keys())
print('candidate keys sample:', sorted(list(cands))[:50])
# pick a likely measurement
for choice in ['object_distance', 'object.distance', 'object.distance', 'object_Bat', 'object_Bat', 'object_bat', 'object.distance']:
    print('\nTrying measurement:', choice)
    rows = []
    for r in full:
        t = r.get('time') or r.get('timestamp') or r.get('ts')
        v = None
        if choice in r:
            v = r.get(choice)
        else:
            # try convert dot to underscore
            v = r.get(choice.replace('.', '_'))
            if v is None:
                # case-insensitive keys
                for k in r.keys():
                    if isinstance(k, str) and k.lower() == choice.replace('.', '_').lower():
                        v = r[k]
                        break
        if t is not None and v is not None:
            rows.append({'time': t, 'value': v})
    print('found rows:', len(rows))
    if rows:
        vis = Visualizer()
        print('calling display_graph')
        vis.display_graph({choice: rows})
        break
print('done')
