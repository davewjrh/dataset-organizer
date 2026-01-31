import sys
sys.path.insert(0, 'src')
from organizer import Organizer
from devices import devices as DEVICE_LIST

o = Organizer()
o.load_data('data/raw/sample_device_1.csv')
o.clean_data()
d = o.organize_by_device()

device_keys = list(d.keys())


def _friendly_label(key):
    label = str(key)
    # map 1-based numeric id to devices list if possible
    try:
        idx = int(key) - 1
        if 0 <= idx < len(DEVICE_LIST):
            return f"{key} ({DEVICE_LIST[idx].name})"
    except Exception:
        pass

    for dev in DEVICE_LIST:
        if str(key) == dev.dev_eui or str(key) == dev.dev_addr or str(key) == dev.gateway_eui or str(key) == dev.name:
            return f"{key} ({dev.name})"
    return label

print('Available devices:')
print('  0) All devices')
for i, dkey in enumerate(device_keys, start=1):
    print(f'  {i}) {_friendly_label(dkey)}')
