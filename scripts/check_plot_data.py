import sys
sys.path.insert(0, 'src')
from organizer import Organizer
from visualizer import Visualizer

# load project sample
o = Organizer()
o.load_data('data/raw/sample_device_1.csv')
o.clean_data()
organized = o.organize_by_device()
print('Devices:', list(organized.keys()))

# pick first device
dev = list(organized.keys())[0]
records = organized.get(dev)
print('Records per device:', len(records))
# list candidate measurements
cand = set()
for r in records:
    cand.update(r.keys())
print('Candidate measurement keys:', sorted(cand))
# find keys with numeric-ish values
num_keys = []
for k in sorted(cand):
    if k in ('device_id','time'):
        continue
    # check a sample of values
    vals = [r.get(k) for r in records[:20]]
    non_null = [v for v in vals if v is not None]
    if not non_null:
        continue
    # test convertible to float
    ok = True
    for v in non_null:
        try:
            float(v)
        except Exception:
            ok = False
            break
    if ok:
        num_keys.append(k)
print('Numeric-looking keys:', num_keys)

# Prepare plot_data similar to GUI do_plot for first numeric key
if num_keys:
    m = num_keys[0]
    rows = []
    for r in records:
        t = r.get('time')
        v = r.get(m)
        if t is None or v is None:
            continue
        rows.append({'time': t, 'value': v})
    print('Built', len(rows), 'rows for measurement', m)
    print('Sample rows:', rows[:5])
    # Try plotting but use save to file to avoid GUI blocking
    vis = Visualizer()
    # Adapted display_graph to save png if requested
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pandas as pd
    df = pd.DataFrame(rows)
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df = df.sort_values('time')
    plt.plot(df['time'], df['value'])
    plt.savefig('test_plot.png')
    print('Saved test_plot.png')
else:
    print('No numeric measurement keys found; nothing to plot')
