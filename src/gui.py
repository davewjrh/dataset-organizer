import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading


def run_gui(organized_data, visualizer, organizer=None, source_used=None, loaded_files=None):
    """Run a simple tkinter GUI for device and measurement selection.

    organized_data: dict mapping device_key -> list[records]
    visualizer: Visualizer instance with display_spreadsheet and display_graph
    organizer: Organizer instance (optional) used for on-demand loads when scan was used
    """
    root = tk.Tk()
    root.title('Dataset Organizer')
    root.geometry('900x650')

    # Ensure closing the main window attempts to clean up plots and threads
    def _on_close():
        try:
            # Close any matplotlib windows to avoid non-daemon GUI threads
            try:
                import matplotlib.pyplot as _plt
                _plt.close('all')
            except Exception:
                pass
            # Destroy any remaining Toplevels
            for w in list(root.winfo_children()):
                try:
                    if isinstance(w, tk.Toplevel):
                        w.destroy()
                except Exception:
                    pass
            try:
                root.quit()
            except Exception:
                pass
            try:
                root.destroy()
            except Exception:
                pass
        finally:
            # As a last-resort, force the process to exit to avoid leaving the
            # terminal stuck (this will immediately terminate Python).
            try:
                import os
                os._exit(0)
            except Exception:
                pass

    root.protocol('WM_DELETE_WINDOW', _on_close)

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    hdr = f"Source: {source_used if source_used else 'project data'}"
    ttk.Label(frame, text=hdr).pack(anchor='w')
    ttk.Label(frame, text=f"Loaded files: {len(loaded_files) if loaded_files else 0}").pack(anchor='w')

    ttk.Label(frame, text='Devices (select one or more):').pack(anchor='w', pady=(10, 0))
    dev_keys = list(organized_data.keys())

    # Try to load known device list for friendly names
    try:
        from devices import devices as DEVICE_LIST
    except Exception:
        DEVICE_LIST = []

    def _extract_folder(first):
        if not first or not isinstance(first, dict):
            return None
        sf = first.get('_source_file')
        if not sf:
            return None
        try:
            p = Path(sf)
            parts = [part for part in p.parts]
            lowered = [part.lower() for part in parts]
            folder = None
            if 'data' in lowered:
                try:
                    di = lowered.index('data')
                    if di + 1 < len(lowered) and lowered[di + 1] == 'raw':
                        if di + 2 < len(parts):
                            folder = parts[di + 2]
                except Exception:
                    pass
            if not folder:
                parent = p.parent.name
                if parent and parent.lower() not in {'data', 'raw', 'processed', 'dataset'}:
                    folder = parent
            if not folder:
                folder = p.stem
            return folder
        except Exception:
            return None

    def _get_nested(first, key):
        if not isinstance(first, dict):
            return None
        if key in first and first.get(key):
            return first.get(key)
        if '.' in key:
            cur = first
            for p in key.split('.'):
                if isinstance(cur, dict) and p in cur:
                    cur = cur[p]
                else:
                    cur = None
                    break
            return cur
        # try lowercase match
        lk = key.lower()
        for kf, v in first.items():
            if kf.lower() == lk and v:
                return v
        return None

    def _get_name_from_record(first):
        if not first or not isinstance(first, dict):
            return None
        candidates = ['deviceName', 'deviceProfileName', 'device_name', 'device_label', 'node_name', 'name']
        blacklist = {'chirpstack', 'the things network', 'ttn', 'lorawan', 'lora'}
        for c in candidates:
            try:
                v = _get_nested(first, c)
                if v:
                    sval = str(v).strip()
                    if sval and sval.lower() not in blacklist:
                        return sval
            except Exception:
                continue
        for kf, v in first.items():
            lk = kf.lower()
            if 'device' in lk and 'name' in lk and v:
                sval = str(v).strip()
                if sval and sval.lower() not in blacklist:
                    return sval
        # match DEVICE_LIST names inside values
        for dev in DEVICE_LIST:
            try:
                dname = dev.name.lower()
                for v in first.values():
                    try:
                        if dname in str(v).lower():
                            return dev.name
                    except Exception:
                        continue
            except Exception:
                continue
        return None

    def _format_label(device_id, folder=None, subname=None):
        parts = []
        if folder:
            parts.append(str(folder))
        if subname:
            parts.append(str(subname))
        parts.append(str(device_id))
        return ' — '.join(parts)

    # Build device labels
    dev_labels = []
    for k in dev_keys:
        label = None
        try:
            records = organized_data.get(k)
            if not records:
                ks = [kk for kk in organized_data.keys() if str(kk) == str(k)]
                if ks:
                    records = organized_data.get(ks[0])
            first = records[0] if records and len(records) > 0 else None
            folder = _extract_folder(first)
            name_candidate = _get_name_from_record(first)
            # If the extracted name is identical to the device id, don't duplicate it
            try:
                if name_candidate and str(name_candidate).strip() == str(k).strip():
                    name_candidate = None
            except Exception:
                pass
            # If the extracted folder equals the device id, don't include it
            try:
                if folder and str(folder).strip() == str(k).strip():
                    folder = None
            except Exception:
                pass
            if folder and name_candidate:
                label = _format_label(k, folder=folder, subname=name_candidate)
            elif name_candidate:
                label = _format_label(k, subname=name_candidate)
            elif folder:
                label = _format_label(k, folder=folder)
            else:
                matched = False
                for dev in DEVICE_LIST:
                    try:
                        if str(k) == dev.dev_eui or str(k) == dev.dev_addr or str(k) == dev.gateway_eui or str(k) == dev.name:
                            label = _format_label(k, subname=dev.name)
                            matched = True
                            break
                    except Exception:
                        continue
                if not matched:
                    label = str(k)
        except Exception:
            label = str(k)
        dev_labels.append(label)

    # UI widgets
    displayed_indices = list(range(len(dev_keys)))

    # container for search + listbox
    dev_container = ttk.Frame(frame)
    dev_container.pack(fill=tk.BOTH, expand=False)

    search_var = tk.StringVar(value='')
    search_frame = ttk.Frame(dev_container)
    ttk.Label(search_frame, text='Search devices:').pack(side=tk.LEFT)
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
    search_frame.pack(fill=tk.X, pady=(0, 6))

    dev_listbox_frame = ttk.Frame(dev_container)
    dev_listbox_frame.pack(fill=tk.BOTH, expand=True)
    dev_listbox = tk.Listbox(dev_listbox_frame, selectmode=tk.MULTIPLE, height=10)
    dev_scroll = ttk.Scrollbar(dev_listbox_frame, orient=tk.VERTICAL, command=dev_listbox.yview)
    dev_listbox.config(yscrollcommand=dev_scroll.set)
    dev_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    dev_scroll.pack(side=tk.LEFT, fill=tk.Y)

    def _repopulate_device_list(filtered_indices=None):
        nonlocal displayed_indices
        # preserve currently selected device keys so selection survives repopulate
        try:
            cur_sel = set()
            for si in dev_listbox.curselection():
                try:
                    cur_key = dev_keys[displayed_indices[si]]
                    cur_sel.add(str(cur_key))
                except Exception:
                    continue
        except Exception:
            cur_sel = set()

        dev_listbox.delete(0, tk.END)
        if filtered_indices is None:
            filtered_indices = list(range(len(dev_labels)))
        displayed_indices = filtered_indices
        for j, i in enumerate(filtered_indices):
            dev_listbox.insert(tk.END, dev_labels[i])
            try:
                if str(dev_keys[i]) in cur_sel:
                    dev_listbox.select_set(j)
            except Exception:
                continue

    _repopulate_device_list()

    def filter_devices(event=None):
        q = search_var.get().strip().lower()
        if not q:
            _repopulate_device_list()
            return
        matches = [i for i, lbl in enumerate(dev_labels) if q in lbl.lower() or q in str(dev_keys[i]).lower()]
        _repopulate_device_list(matches)

    search_entry.bind('<KeyRelease>', filter_devices)

    # helper: collect nested keys and access nested values
    def _collect_keys_from_record(rec, prefix=''):
        """Recursively collect keys from a possibly nested dict record.

        Returns a set of dot-notated key names (e.g. payload.temperature).
        """
        keys = set()
        if isinstance(rec, dict):
            for kk, vv in rec.items():
                if kk.startswith('_'):
                    continue
                new_key = f"{prefix}.{kk}" if prefix else kk
                if isinstance(vv, dict):
                    keys.update(_collect_keys_from_record(vv, new_key))
                elif isinstance(vv, list):
                    # If we have a list of dicts (e.g. rxInfo), inspect elements
                    for it in vv:
                        if isinstance(it, dict):
                            keys.update(_collect_keys_from_record(it, new_key))
                        else:
                            # non-dict list elements are treated as a value for the list key
                            keys.add(new_key)
                else:
                    keys.add(new_key)
        return keys

    def _get_nested_value(rec, key):
        """Get a nested value from a record using dot notation.

        Returns None if any part is missing.
        """
        if not isinstance(rec, dict):
            return None
        if key in rec:
            return rec.get(key)
        if '.' in key:
            cur = rec
            for part in key.split('.'):
                if isinstance(cur, dict) and part in cur:
                    cur = cur[part]
                    continue
                # If current node is a list, try to find the part in any element
                if isinstance(cur, list):
                    found = None
                    for it in cur:
                        if isinstance(it, dict) and part in it:
                            found = it[part]
                            break
                    if found is None:
                        return None
                    cur = found
                    continue
                # not found
                return None
            return cur
        # also try underscore variant (some loaders normalize '.' -> '_')
        try:
            alt = key.replace('.', '_')
            if alt in rec:
                return rec.get(alt)
        except Exception:
            pass
        lk = key.lower()
        for kf, v in rec.items():
            if kf.lower() == lk:
                return v
        return None

    # Measurements list
    ttk.Label(frame, text='Measurements (select one or more):').pack(anchor='w', pady=(10, 0))
    meas_frame = ttk.Frame(frame)
    meas_frame.pack(fill=tk.BOTH, expand=False)
    meas_listbox = tk.Listbox(meas_frame, selectmode=tk.MULTIPLE, height=8)
    meas_scroll = ttk.Scrollbar(meas_frame, orient=tk.VERTICAL, command=meas_listbox.yview)
    meas_listbox.config(yscrollcommand=meas_scroll.set)
    meas_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    meas_scroll.pack(side=tk.LEFT, fill=tk.Y)
    
    def populate_measurements():
        sel = dev_listbox.curselection()
        if not sel:
            messagebox.showinfo('Selection', 'Please select at least one device first')
            return
        visible_keys = []
        for i in sel:
            try:
                real_idx = displayed_indices[i]
            except Exception:
                real_idx = i
            visible_keys.append(dev_keys[real_idx])

        candidate_keys = set()

        def _update_meas():
            candidate_keys.clear()
            for k in visible_keys:
                records = organized_data.get(k, [])
                for rec in records:
                    candidate_keys.update(_collect_keys_from_record(rec))
            # If any collected key corresponds to a list-of-dicts (e.g. rxinfo),
            # add explicit subkeys for the first element so users can select rssi/snr etc.
            extra = set()
            for k in list(candidate_keys):
                # look at sample records to see if this key is a list
                for rec in (organized_data.get(visible_keys[0], []) or [])[:5]:
                    try:
                        val = _get_nested_value(rec, k)
                        if isinstance(val, list) and val:
                            first = val[0]
                            if isinstance(first, dict):
                                for subk in first.keys():
                                    extra.add(f"{k}.{subk}")
                    except Exception:
                        continue
            candidate_keys.update(extra)
            exclude = {'device_id', 'time', 'device', 'Device', '_source_file'}
            candidates = [m for m in sorted(candidate_keys) if m not in exclude]
            meas_listbox.delete(0, tk.END)
            for m in candidates:
                meas_listbox.insert(tk.END, m)

        keys_to_load = []
        if organizer is not None and getattr(organizer, '_scanned', False):
            for k in visible_keys:
                if hasattr(organizer, '_device_folder_map') and k in organizer._device_folder_map:
                    if not organized_data.get(k) or any(not isinstance(r, dict) or '_source_file' not in r for r in organized_data.get(k, [])):
                        keys_to_load.append(k)

        if keys_to_load:
            progress = tk.Toplevel(root)
            progress.title('Loading...')
            ttk.Label(progress, text='Loading device data, please wait...').pack(padx=10, pady=10)

            def worker():
                for k in keys_to_load:
                    try:
                        full = organizer.load_device_full(k)
                        if full:
                            organized_data[k] = full
                    except Exception:
                        continue
                root.after(50, lambda: (progress.destroy(), _update_meas()))

            threading.Thread(target=worker, daemon=True).start()
        else:
            _update_meas()

        def _update_meas():
            candidate_keys.clear()
            # Collect keys across all records for selected devices
            for k in visible_keys:
                records = organized_data.get(k, [])
                for rec in records:
                    candidate_keys.update(_collect_keys_from_record(rec))
            exclude = {'device_id', 'time', 'device', 'Device', '_source_file'}
            candidates = [m for m in sorted(candidate_keys) if m not in exclude]
            meas_listbox.delete(0, tk.END)
            for m in candidates:
                meas_listbox.insert(tk.END, m)

        keys_to_load = []
        if organizer is not None and getattr(organizer, '_scanned', False):
            for k in visible_keys:
                if hasattr(organizer, '_device_folder_map') and k in organizer._device_folder_map:
                    if not organized_data.get(k) or any(not isinstance(r, dict) or '_source_file' not in r for r in organized_data.get(k, [])):
                        keys_to_load.append(k)

        if keys_to_load:
            progress = tk.Toplevel(root)
            progress.title('Loading...')
            ttk.Label(progress, text='Loading device data, please wait...').pack(padx=10, pady=10)

            def worker():
                for k in keys_to_load:
                    try:
                        full = organizer.load_device_full(k)
                        if full:
                            organized_data[k] = full
                    except Exception:
                        continue
                root.after(50, lambda: (progress.destroy(), _update_meas()))

            threading.Thread(target=worker, daemon=True).start()
        else:
            _update_meas()

    ttk.Button(frame, text='Refresh Measurements', command=populate_measurements).pack(pady=6)

    # Display option
    display_var = tk.StringVar(value='graph')
    disp_frame = ttk.Frame(frame)
    ttk.Radiobutton(disp_frame, text='Graph', variable=display_var, value='graph').pack(side=tk.LEFT)
    ttk.Radiobutton(disp_frame, text='Spreadsheet', variable=display_var, value='spreadsheet').pack(side=tk.LEFT)
    disp_frame.pack(anchor='w', pady=(10, 0))

    def get_selected_devices():
        sel = dev_listbox.curselection()
        keys = [dev_keys[displayed_indices[i]] for i in sel] if sel else []
        if not keys:
            keys = dev_keys
        return keys

    def get_selected_measurements():
        sel = meas_listbox.curselection()
        return [meas_listbox.get(i) for i in sel]

    def do_spreadsheet():
        keys = get_selected_devices()
        keys_to_load = []
        if organizer is not None and getattr(organizer, '_scanned', False):
            for k in keys:
                if hasattr(organizer, '_device_folder_map') and k in organizer._device_folder_map:
                    if not organized_data.get(k) or any(not isinstance(r, dict) or '_source_file' not in r for r in organized_data.get(k, [])):
                        keys_to_load.append(k)

        def _do_export():
            selected_data = {k: organized_data[k] for k in keys}
            visualizer.display_spreadsheet(selected_data)
            messagebox.showinfo('Export', 'Spreadsheet saved (see output.csv)')

        if keys_to_load:
            progress = tk.Toplevel(root)
            progress.title('Loading...')
            ttk.Label(progress, text='Loading device data, please wait...').pack(padx=10, pady=10)

            def worker():
                for k in keys_to_load:
                    try:
                        full = organizer.load_device_full(k)
                        if full:
                            organized_data[k] = full
                    except Exception:
                        continue
                root.after(50, lambda: (progress.destroy(), _do_export()))

            threading.Thread(target=worker, daemon=True).start()
        else:
            _do_export()

    def do_plot():
        keys = get_selected_devices()
        measurements = get_selected_measurements()
        if not measurements:
            messagebox.showinfo('Selection', 'Please select at least one measurement to plot')
            return

        keys_to_load = []
        if organizer is not None and getattr(organizer, '_scanned', False):
            for k in keys:
                if hasattr(organizer, '_device_folder_map') and k in organizer._device_folder_map:
                    if not organized_data.get(k) or any(not isinstance(r, dict) or '_source_file' not in r for r in organized_data.get(k, [])):
                        keys_to_load.append(k)

        def _build_and_plot():
            plot_data = {}
            excluded = []
            for k in keys:
                records = organized_data.get(k, [])
                for m in measurements:
                    rows = []
                    for r in records:
                        # try common time fields and fall back to None
                        t = _get_nested_value(r, 'time') or _get_nested_value(r, 'timestamp') or _get_nested_value(r, 'ts')
                        # allow dot/underscore alternative for measurement key
                        v = _get_nested_value(r, m) or _get_nested_value(r, m.replace('.', '_'))
                        if t is None or v is None:
                            continue
                        rows.append({'time': t, 'value': v})
                    # debug: show how many rows were found for this series
                    try:
                        print(f"Series {k} - {m}: found {len(rows)} rows")
                    except Exception:
                        pass
                    if not rows:
                        excluded.append(f"{k} - {m}")
                        continue

                    # Attempt to clean and validate time/value using pandas if available
                    try:
                        import pandas as _pd
                        df = _pd.DataFrame(rows)
                        # normalize time and numeric value similar to visualizer
                        try:
                            df['time'] = _pd.to_datetime(df['time'], errors='coerce')
                        except Exception:
                            df['time'] = _pd.to_datetime(df['time'], errors='coerce')
                        df['value'] = _pd.to_numeric(df['value'], errors='coerce')
                        df = df.dropna(subset=['time', 'value'])
                        if df.empty:
                            excluded.append(f"{k} - {m}")
                            continue
                        df = df.sort_values('time')
                        series_key = f"{k} - {m}" if len(measurements) > 1 else str(k)
                        plot_data[series_key] = df.to_dict(orient='records')
                    except Exception:
                        # If pandas is unavailable or conversion fails, fall back to raw rows
                        series_key = f"{k} - {m}" if len(measurements) > 1 else str(k)
                        plot_data[series_key] = rows

            if not plot_data:
                msg = 'No plottable data found for selection.'
                if excluded:
                    msg += '\nExcluded series:\n' + '\n'.join(excluded[:50])
                messagebox.showinfo('No data', msg)
                return

            if excluded:
                try:
                    print('Excluded empty series:')
                    for e in excluded:
                        print(' -', e)
                except Exception:
                    pass

            visualizer.display_graph(plot_data)

        if keys_to_load:
            progress = tk.Toplevel(root)
            progress.title('Loading...')
            ttk.Label(progress, text='Loading device data, please wait...').pack(padx=10, pady=10)

            def worker():
                for k in keys_to_load:
                    try:
                        full = organizer.load_device_full(k)
                        if full:
                            organized_data[k] = full
                    except Exception:
                        continue
                root.after(50, lambda: (progress.destroy(), _build_and_plot()))

            threading.Thread(target=worker, daemon=True).start()
        else:
            _build_and_plot()

    btn_frame = ttk.Frame(frame)
    ttk.Button(btn_frame, text='Show Spreadsheet', command=do_spreadsheet).pack(side=tk.LEFT, padx=4)
    ttk.Button(btn_frame, text='Plot Graph', command=do_plot).pack(side=tk.LEFT, padx=4)
    ttk.Button(btn_frame, text='Quit', command=_on_close).pack(side=tk.LEFT, padx=4)
    btn_frame.pack(pady=12)

    root.mainloop()
        
