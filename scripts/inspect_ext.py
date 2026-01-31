import sys
sys.path.insert(0, 'src')
from organizer import Organizer

ext = r'C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset'
o = Organizer()
df = o.load_all_from_dir(ext)
print('shape', getattr(df, 'shape', None))
cols = list(df.columns)
print('columns (first 80):')
for c in cols[:80]:
    print(c)
print('\nloaded files (sample 10):')
print(getattr(o, '_loaded_files', [])[:10])
