import sys
import importlib.util
sys.path.insert(0, 'src')
from organizer import Organizer

ext_dir = r'C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset'
print('Loading external dataset (may take a few seconds)...')
o = Organizer()
_df = o.load_all_from_dir(ext_dir)
if _df is None:
    print('No files found in external dir')
    sys.exit(1)
o.clean_data()
organized = o.organize_by_device()
keys = list(organized.keys())
print('Found', len(keys), 'devices; sample keys:')
print(keys[:20])

# load gui module directly from file to avoid package-level side effects
spec = importlib.util.spec_from_file_location('gui_mod', 'src/gui.py')
gui_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gui_mod)

labels = [gui_mod._friendly_label(k) for k in keys[:50]]
print('\nSample labels:')
for lbl in labels[:50]:
    print(' -', lbl)
