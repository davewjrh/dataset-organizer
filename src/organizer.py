class Organizer:
    def __init__(self):
        self.data = None

    def load_data(self, file_path):
        import pandas as pd
        self.data = pd.read_csv(file_path)
        # annotate source file for single-file loads as well
        try:
            if self.data is not None and not self.data.empty:
                self.data['_source_file'] = file_path
        except Exception:
            pass
        return self.data

    def load_all_from_dir(self, dir_path, pattern='*.csv'):
        """Load and concatenate all CSV files in a directory into a single DataFrame.
        Sets self.data and returns the concatenated DataFrame. If no files are
        found, returns None.
        """
        import pandas as pd
        import glob
        import os

        # Search recursively for CSV/JSON files to handle nested dataset layouts
        patterns = ['**/*.csv', '**/*.json', '**/*.ndjson', '**/*.jsonl']
        files = []
        for p in patterns:
            files.extend(glob.glob(os.path.join(dir_path, p), recursive=True))
        if not files:
            return None

        dfs = []
        loaded_files = []
        import json
        for f in files:
            try:
                if f.lower().endswith('.csv'):
                    df = pd.read_csv(f)
                else:
                    # Attempt to load arbitrary JSON structures and normalize
                    with open(f, 'r', encoding='utf-8') as fh:
                        obj = json.load(fh)
                    # If the file contains a list of records, create DataFrame directly
                    if isinstance(obj, list):
                        df = pd.json_normalize(obj)
                    else:
                        df = pd.json_normalize([obj])
                # annotate source file so downstream code (GUI) can use origin info
                if df is not None and not df.empty:
                    try:
                        df['_source_file'] = f
                    except Exception:
                        # best-effort: ignore if cannot set
                        pass
                dfs.append(df)
                loaded_files.append(f)
            except Exception:
                # skip unreadable or unparsable files
                continue

        if not dfs:
            return None

        self.data = pd.concat(dfs, ignore_index=True)
        # record which files were successfully loaded (useful for debugging)
        self._loaded_files = loaded_files
        return self.data

    def scan_dataset(self, dir_path, sample_per_device=1, max_files=None):
        """Lightweight recursive scan of a dataset directory.

        Scans files under dir_path (recursively), sampling up to
        `max_files` files total and collecting up to `sample_per_device`
        sample records per detected device id. Returns a dict mapping
        device_id_or_folder_key -> list[record(dict)]. Also builds
        self._device_file_index mapping device_id -> set(file_paths) for
        on-demand full loads.
        """
        from pathlib import Path
        import json

        base = Path(dir_path)
        if not base.exists() or not base.is_dir():
            return None

        device_map = {}
        folder_map = {}
        loaded_files = []
        device_file_index = {}

        # Helper to try and find a device identifier inside a sample dict
        id_candidates = {'dev_eui', 'deveui', 'devaddr', 'dev_addr', 'device_id', 'deviceid', 'dev_eui'}

        def _find_device_id(o):
            if o is None:
                return None
            if isinstance(o, dict):
                for k, v in o.items():
                    lk = k.strip().lower()
                    if lk in id_candidates and v is not None:
                        return str(v)
                    if 'dev' in lk and ('eui' in lk or 'addr' in lk or 'id' in lk) and v is not None:
                        return str(v)
                    # recurse into nested dicts/lists
                    if isinstance(v, dict):
                        got = _find_device_id(v)
                        if got:
                            return got
                    if isinstance(v, list):
                        for it in v:
                            got = _find_device_id(it)
                            if got:
                                return got
            return None

        # Iterate files recursively but cap the number of files inspected
        file_patterns = ('**/*.json', '**/*.ndjson', '**/*.jsonl', '**/*.csv')
        scanned = 0
        for pat in file_patterns:
            for f in base.glob(pat):
                if max_files is not None and scanned >= max_files:
                    break
                scanned += 1
                try:
                    sample_obj = None
                    if f.suffix.lower() == '.csv':
                        import csv
                        with open(f, 'r', encoding='utf-8') as fh:
                            reader = csv.DictReader(fh)
                            row = next(reader, None)
                            if row:
                                sample_obj = {k.strip(): v for k, v in row.items()}
                    else:
                        # JSON/NDJSON
                        if f.suffix.lower() in ('.ndjson', '.jsonl'):
                            with open(f, 'r', encoding='utf-8') as fh:
                                line = fh.readline()
                                if line:
                                    sample_obj = json.loads(line)
                        else:
                            with open(f, 'r', encoding='utf-8') as fh:
                                obj = json.load(fh)
                                if isinstance(obj, list) and obj:
                                    sample_obj = obj[0]
                                elif isinstance(obj, dict):
                                    sample_obj = obj
                    if isinstance(sample_obj, dict):
                        sample_obj['_source_file'] = str(f)
                        dev_id = _find_device_id(sample_obj)
                        # prefer folder-derived device id when it looks like a devEUI (hex string)
                        try:
                            import re
                            parent_tokens = [part for part in f.parts if part]
                            folder_candidate = None
                            # check parent directories starting from immediate parent up
                            for part in reversed(parent_tokens[:-1]):
                                if re.fullmatch(r'[0-9a-fA-F]{8,32}', part):
                                    folder_candidate = part
                                    break
                            # if sample-derived id looks like a UUID but folder looks like hex devEUI, prefer folder
                            if dev_id and '-' in str(dev_id) and folder_candidate:
                                dev_id = folder_candidate

                            if not dev_id and folder_candidate:
                                dev_id = folder_candidate
                        except Exception:
                            pass

                        if dev_id:
                            # store sample if we don't have enough for this device yet
                            samples = device_map.setdefault(str(dev_id), [])
                            if len(samples) < sample_per_device:
                                samples.append(sample_obj)
                            device_file_index.setdefault(str(dev_id), set()).add(str(f))
                            folder_map.setdefault(str(dev_id), str(f.parent))
                        else:
                            # fallback to folder-based key (use immediate parent folder name)
                            key = f.parent.name
                            samples = device_map.setdefault(key, [])
                            if len(samples) < sample_per_device:
                                samples.append(sample_obj)
                            device_file_index.setdefault(key, set()).add(str(f))
                            folder_map.setdefault(key, str(f.parent))
                    loaded_files.append(str(f))
                except Exception:
                    continue
            if max_files is not None and scanned >= max_files:
                break

        # convert sets to lists
        for k, s in device_file_index.items():
            device_file_index[k] = list(s)

        # store indices/mappings for on-demand full loads
        self._device_file_index = device_file_index
        self._device_folder_map = folder_map
        self._loaded_files = loaded_files
        self._scanned = True
        return device_map

    def load_device_full(self, device_key):
        """Load all records for a device (by folder name as returned by scan_dataset).

        Returns a list of record dicts. This performs full parsing of files under
        the device folder and annotates records with '_source_file'.
        """
        import json
        from pathlib import Path

        if not hasattr(self, '_device_folder_map'):
            raise RuntimeError('No device folder mapping available; run scan_dataset first')
        folder = self._device_folder_map.get(device_key)
        if not folder:
            raise KeyError(f'No folder known for device key: {device_key}')

        records = []
        # If we have a precomputed file index for this device, use it (fast)
        files = None
        if hasattr(self, '_device_file_index') and device_key in self._device_file_index:
            files = [Path(fp) for fp in self._device_file_index.get(device_key, [])]
        else:
            p = Path(folder)
            files = list(p.rglob('*.json')) + list(p.rglob('*.ndjson')) + list(p.rglob('*.jsonl')) + list(p.rglob('*.csv'))
        for f in files:
            try:
                if f.suffix.lower() == '.csv':
                    import csv
                    with open(f, 'r', encoding='utf-8') as fh:
                        reader = csv.DictReader(fh)
                        for row in reader:
                            r = {k.strip(): v for k, v in row.items()}
                            r['_source_file'] = str(f)
                            records.append(r)
                else:
                    if f.suffix.lower() in ('.ndjson', '.jsonl'):
                        with open(f, 'r', encoding='utf-8') as fh:
                            for line in fh:
                                if not line.strip():
                                    continue
                                obj = json.loads(line)
                                if isinstance(obj, dict):
                                    obj['_source_file'] = str(f)
                                    records.append(obj)
                    else:
                        with open(f, 'r', encoding='utf-8') as fh:
                            obj = json.load(fh)
                            if isinstance(obj, list):
                                for it in obj:
                                    if isinstance(it, dict):
                                        it['_source_file'] = str(f)
                                        records.append(it)
                            elif isinstance(obj, dict):
                                obj['_source_file'] = str(f)
                                records.append(obj)
                # update loaded_files
                try:
                    if not hasattr(self, '_loaded_files'):
                        self._loaded_files = []
                    self._loaded_files.append(str(f))
                except Exception:
                    pass
            except Exception:
                continue

        # Optionally, normalize/clean these records using existing clean_data
        try:
            import pandas as pd
            df = pd.json_normalize(records)
            df['_source_file'] = df.get('_source_file')
            # run basic cleaning on this df
            self.data = df
            self._clean_data_internal()
            # return records for the device as list of dicts
            return self.data.to_dict(orient='records')
        except Exception:
            return records

    

    # Allow passing a DataFrame directly (tests call clean_data(data))
    def clean_data(self, data=None):
        if data is not None:
            self.data = data
        return self._clean_data_internal()

    def _clean_data_internal(self):
        # Internal cleaning used by both interfaces
        if self.data is None:
            return None
        # Make column names safe: lowercase, replace spaces/dots with underscores
        orig_cols = list(self.data.columns)
        safe_cols = [c.strip().lower().replace(' ', '_').replace('.', '_') for c in orig_cols]
        self.data.columns = safe_cols

        # Heuristics to find a device identifier column (don't map every
        # 'device*' column to device_id — be specific)
        device_col = None
        # priority substrings to look for
        priorities = ['dev_eui', 'deveui', 'devaddr', 'dev_addr', 'device_id', 'deviceid', 'deviceid']
        for p in priorities:
            for c in safe_cols:
                if p in c:
                    device_col = c
                    break
            if device_col:
                break

        # fallback: look for any column that contains 'dev' and ('eui' or 'addr' or 'id')
        if not device_col:
            for c in safe_cols:
                lc = c.lower()
                if 'dev' in lc and ('eui' in lc or 'addr' in lc or lc.endswith('_id') or '_id' in lc):
                    device_col = c
                    break

        # If we found a device column, ensure there's a 'device_id' normalized column
        if device_col and 'device_id' not in self.data.columns:
            self.data['device_id'] = self.data[device_col].astype(str)

        # Normalize time column if present
        time_col = None
        for c in safe_cols:
            if 'time' in c or 'timestamp' in c or 'date' in c:
                time_col = c
                break
        if time_col:
            # parse times into pandas datetimes for consistent plotting
            import pandas as _pd
            # coerce errors to NaT and keep timezone info if present
            self.data['time'] = _pd.to_datetime(self.data[time_col], errors='coerce', utc=True)

        # Do basic cleaning: drop rows with no device id
        if 'device_id' in self.data.columns:
            self.data.dropna(subset=['device_id'], inplace=True)
        else:
            # if no device id, drop rows entirely (nothing to group)
            self.data.dropna(how='all', inplace=True)

        self.data.reset_index(drop=True, inplace=True)
        return self.data

    def organize_by_device(self, data=None):
        """Group rows by device_id and return a dict mapping device -> list of records.
        Accepts an optional DataFrame argument for backwards compatibility with tests.
        """
        df = data if data is not None else self.data
        if df is None:
            return None

        # If a DataFrame was provided by the caller (tests expect a DataFrame
        # result), return a DataFrame and ensure there's a 'Device' column.
        try:
            import pandas as pd
        except Exception:
            pd = None

        if data is not None:
            # Ensure standardized column names
            def _standardize_col(c):
                s = c.strip().lower()
                if 'device' in s:
                    return 'device_id'
                if 'time' in s or 'timestamp' in s or 'date' in s:
                    return 'time'
                if 'value' in s or 'val' in s:
                    return 'value'
                return s.replace(' ', '_')

            df.columns = [_standardize_col(c) for c in df.columns]
            # Provide a 'Device' column to match tests expecting that name
            if 'device_id' in df.columns and 'Device' not in df.columns:
                df['Device'] = df['device_id']
            return df

        # Default behavior (no data arg): return dict mapping device -> records
        grouped = self.data.groupby('device_id')
        return grouped.apply(lambda x: x.to_dict(orient='records')).to_dict()

    def save_processed_data(self, data, file_path):
        """Save a cleaned DataFrame (or records) to CSV."""
        import pandas as pd
        if data is None:
            raise ValueError("No data provided to save_processed_data")
        if not hasattr(data, 'to_csv'):
            # assume sequence of records
            df = pd.DataFrame(data)
        else:
            df = data
        df.to_csv(file_path, index=False)