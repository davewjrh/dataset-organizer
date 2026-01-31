import sys
sys.path.insert(0, r'c:\Users\davew\OneDrive - Carleton University\Workspace\dataset-organizer\src')
from organizer import Organizer
from visualizer import Visualizer
import tkinter as tk

org = Organizer()
sc = org.scan_dataset(r'c:\Users\davew\OneDrive - Carleton University\Workspace\dataset-organizer\data\raw', sample_per_device=1, max_files=200)
key = list(sc.keys())[0]
full = org.load_device_full(key)
# build rows for rxinfo.rssi
rows = []
for r in full:
    t = r.get('time')
    # rxinfo may be list
    if 'rxinfo' in r and isinstance(r['rxinfo'], list) and r['rxinfo']:
        first = r['rxinfo'][0]
        v = first.get('rssi') if isinstance(first, dict) else None
    else:
        v = None
    if t is not None and v is not None:
        rows.append({'time': t, 'value': v})
print('rows for rxinfo.rssi:', len(rows))
root = tk.Tk()
vis = Visualizer()
vis.display_graph({'rxinfo.rssi': rows})
print('display_graph returned')
root.destroy()
