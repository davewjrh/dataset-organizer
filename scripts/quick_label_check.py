import sys
sys.path.insert(0, 'src')
from organizer import Organizer
from devices import devices as DEVICE_LIST

print('Loading sample file...')
o = Organizer()
try:
    df = o.load_data('data/raw/sample_device_1.csv')
except Exception as e:
    print('Failed to load sample file:', e)
    sys.exit(1)

o.clean_data()
organized = o.organize_by_device()
keys = list(organized.keys())
print('dev_keys:', keys)

def friendly_label(key):
    label = str(key)
    try:
        idx = int(key) - 1
        if 0 <= idx < len(DEVICE_LIST):
            return f"{DEVICE_LIST[idx].name} ({key})"
    except Exception:
        pass
    for dev in DEVICE_LIST:
        try:
            if str(key) == dev.dev_eui or str(key) == dev.dev_addr or str(key) == dev.gateway_eui or str(key) == dev.name:
                return f"{dev.name} ({key})"
        except Exception:
            continue
    return label

labels = [friendly_label(k) for k in keys]
print('labels:', labels)
