import sys
sys.path.insert(0, 'src')
from organizer import Organizer

# adjust this path if different
ext_dir = r'C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset'

print('Loading external dataset (this may take a few seconds)...')
o = Organizer()
o.load_all_from_dir(ext_dir)
o.clean_data()
organized = o.organize_by_device()

dev_keys = list(organized.keys())
print('Found', len(dev_keys), 'devices; sample keys:')
print(dev_keys[:10])

from devices import devices as DEVICE_LIST

def _friendly_label(key):
    label = str(key)
    try:
        idx = int(key) - 1
        if 0 <= idx < len(DEVICE_LIST):
            return f"{key} ({DEVICE_LIST[idx].name})"
    except Exception:
        pass
    for dev in DEVICE_LIST:
        try:
            if str(key) == dev.dev_eui or str(key) == dev.dev_addr or str(key) == dev.gateway_eui or str(key) == dev.name:
                return f"{key} ({dev.name})"
        except Exception:
            continue
    return label

labels = [_friendly_label(k) for k in dev_keys]
print('Sample labels:')
for lbl in labels[:20]:
    print(' -', lbl)
