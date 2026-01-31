# main.py

import sys
from organizer import Organizer
from visualizer import Visualizer

def main():
    # Initialize the Organizer and Visualizer
    organizer = Organizer()
    visualizer = Visualizer()

    # Load and clean data: prefer processed files (already cleaned) and merge
    # all CSVs found there. If none, fall back to raw files (and merge them).
    import os

    processed_dir = os.path.join('data', 'processed')
    raw_dir = os.path.join('data', 'raw')

    # If you have an external dataset repository on the same machine, prefer
    # loading from there first. This does not move files — it only reads them
    # at runtime. To actually copy the files into this project, see the
    # suggested PowerShell command in the README or below.
    external_dataset_dir = r"C:\Users\davew\OneDrive - Carleton University\Repositories\computer-networks-hackathon-ssi-canada\dataset"

    data_loaded = None
    try:
        if os.path.exists(external_dataset_dir):
            # Perform a fast scan instead of loading all files to avoid
            # expensive full normalization at startup. GUI can request
            # per-device full loads on demand.
            scanned = organizer.scan_dataset(external_dataset_dir)
            if scanned:
                data_loaded = scanned
                source_used = external_dataset_dir
    except Exception:
        data_loaded = None

    source_used = None
    if data_loaded is None:
        data_loaded = organizer.load_all_from_dir(processed_dir)
        source_used = processed_dir if data_loaded is not None else None
    if data_loaded is None:
        # Try raw dir
        data_loaded = organizer.load_all_from_dir(raw_dir)
        source_used = raw_dir if data_loaded is not None else None
        if data_loaded is None:
            # Fallback to single sample path (existing behavior)
            organizer.load_data('data/raw/sample_device_1.csv')
            source_used = 'data/raw/sample_device_1.csv'
    # If we performed a fast scan, data_loaded is a lightweight mapping
    # folder -> [sample_records]. Otherwise we have a full DataFrame in
    # organizer.data and should run the normal clean/organize flow.
    if isinstance(data_loaded, dict):
        organized_data = data_loaded
    else:
        # Clean data (works on self.data and returns the cleaned DataFrame)
        organizer.clean_data()
        organized_data = organizer.organize_by_device()

    # Inform the user where data came from and how many devices were found
    try:
        loaded_files = getattr(organizer, '_loaded_files', None)
        if loaded_files:
            print(f"Loaded {len(loaded_files)} files from: {source_used}")
    except Exception:
        pass
    try:
        if isinstance(organized_data, dict):
            print(f"Found {len(organized_data)} devices in data.")
        elif hasattr(organized_data, 'shape'):
            # DataFrame
            print(f"Loaded DataFrame with shape {organized_data.shape}")
    except Exception:
        pass

    # Launch GUI for all user selection
    try:
        from gui import run_gui
    except Exception:
        print('GUI components unavailable; falling back to command-line prompts')
        # If GUI cannot be imported, keep CLI behavior (simple fallback)
        display_option = input("How would you like to display the data? (spreadsheet/graph): ").strip().lower()
        # Present available devices and let the user choose which to present
        if not organized_data:
            print("No device data available to display.")
            sys.exit(1)
        device_keys = list(organized_data.keys())
        print("Available devices:")
        print("  0) All devices")
        for i, d in enumerate(device_keys, start=1):
            print(f"  {i}) {d}")
        sel = input("Select a device by number (e.g. 1) or 0 for all: ").strip()
        try:
            sel_idx = int(sel)
        except ValueError:
            print("Invalid selection. Please enter a number.")
            sys.exit(1)
        if sel_idx == 0:
            selected_data = organized_data
        elif 1 <= sel_idx <= len(device_keys):
            key = device_keys[sel_idx - 1]
            selected_data = {key: organized_data[key]}
        else:
            print("Selection out of range.")
            sys.exit(1)
        if display_option == 'spreadsheet':
            visualizer.display_spreadsheet(selected_data)
        elif display_option == 'graph':
            visualizer.display_graph(selected_data)
        else:
            print("Invalid option. Please choose 'spreadsheet' or 'graph'.")
            sys.exit(1)
    else:
        # run GUI with organized data
        # pass organizer to GUI so it can perform on-demand full loads when
        # the dataset was scanned (fast startup)
        run_gui(organized_data, visualizer, organizer=organizer, source_used=source_used, loaded_files=getattr(organizer, '_loaded_files', None))
        # Ensure process exits after GUI is closed (some backends may leave
        # non-daemon threads running); explicitly exit to return control to shell.
        try:
            sys.exit(0)
        except SystemExit:
            raise

if __name__ == "__main__":
    main()