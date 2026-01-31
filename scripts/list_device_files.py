from pathlib import Path
ROOT = Path(r"C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset")
for p in sorted([x for x in ROOT.iterdir() if x.is_dir()], key=lambda x: x.name.lower()):
    count = sum(1 for _ in p.rglob('*') if _.is_file())
    print(p.name, count)
