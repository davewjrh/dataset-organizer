class Visualizer:
    """Visualizer that can accept data at construction time or when calling
    display methods. Handles both pandas.DataFrame and organizer-style
    dict-of-records (device_id -> list[dict]) inputs.
    """

    def __init__(self, data=None):
        self.data = data

    def display_spreadsheet(self, data=None, output_path='output.csv'):
        """Save data to a CSV file. Accepts a DataFrame or a dict produced by
        Organizer.organize_by_device()."""
        import pandas as pd

        data = data if data is not None else self.data
        if data is None:
            print("No data provided to display_spreadsheet().")
            return

        # If data is a dict mapping device -> list[records], flatten it
        if isinstance(data, dict):
            rows = []
            for device, records in data.items():
                for r in records:
                    row = dict(r)  # copy
                    # add a device column if not present
                    if 'device_id' not in row:
                        row['device_id'] = device
                    rows.append(row)
            df = pd.DataFrame(rows)
        else:
            # Assume it's DataFrame-like
            try:
                df = pd.DataFrame(data)
            except Exception:
                print("Unsupported data format for display_spreadsheet().")
                return

        df.to_csv(output_path, index=False)
        print(f"Data has been written to {output_path}")

    def display_graph(self, data=None):
        """Plot time-series data. Expects either a dict of device -> list[records]
        where each record has 'time' and 'value' keys, or a DataFrame with
        columns ['device_id','time','value'].'"""
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
        except Exception:
            print("matplotlib and pandas are required for display_graph().")
            return

        data = data if data is not None else self.data
        if data is None:
            print("No data provided to display_graph().")
            return

        # Normalize to device -> DataFrame
        device_frames = {}
        if isinstance(data, dict):
            for device, records in data.items():
                try:
                    df = pd.DataFrame(records)
                except Exception:
                    continue
                device_frames[device] = df
        else:
            df = pd.DataFrame(data)
            if 'device_id' in df.columns:
                for device, group in df.groupby('device_id'):
                    device_frames[device] = group
            else:
                # Single-device DataFrame
                device_frames['data'] = df

        if not device_frames:
            print("No plottable data found in provided input.")
            return

        # Start with a fresh figure to avoid retaining previous plots
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
            fig = plt.figure(figsize=(8, 4))
            ax = fig.add_subplot(1, 1, 1)
        except Exception:
            print('Failed to initialize matplotlib figure.')
            return

        for device, df in device_frames.items():
            if 'time' in df.columns and 'value' in df.columns:
                # Normalize time -> tz-naive UTC datetimes and ensure numeric values
                try:
                    import pandas as _pd
                    from pandas.api.types import is_datetime64_any_dtype, is_datetime64tz_dtype
                    # Convert timezone-aware datetimes to UTC and make them naive
                    try:
                        if is_datetime64tz_dtype(df['time']):
                            df['time'] = df['time'].dt.tz_convert('UTC').dt.tz_localize(None)
                        elif not is_datetime64_any_dtype(df['time']):
                            df['time'] = _pd.to_datetime(df['time'], errors='coerce')
                    except Exception:
                        df['time'] = _pd.to_datetime(df['time'], errors='coerce')

                    # Coerce values to numeric where possible
                    df['value'] = _pd.to_numeric(df['value'], errors='coerce')

                    # Drop rows where time or value could not be parsed
                    df = df.dropna(subset=['time', 'value'])

                    df = df.sort_values('time')
                except Exception:
                    # If conversion fails, skip plotting this device
                    print(f"Skipping device {device}: failed to parse time/value for plotting")
                    continue
                ax.plot(df['time'].values, df['value'].values, label=str(device))
            else:
                print(f"Skipping device {device}: missing 'time' or 'value' columns.")

        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.set_title('Device Data Visualization')
        ax.legend()
        # If running inside the Tkinter GUI mainloop, embed the matplotlib
        # figure in a new Toplevel window so the plot appears reliably.
        try:
            import tkinter as _tk
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
            root = getattr(_tk, '_default_root', None)
            if root is not None:
                fig = plt.gcf()
                win = _tk.Toplevel(root)
                win.title('Plot')
                canvas = FigureCanvasTkAgg(fig, master=win)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=_tk.BOTH, expand=True)
                try:
                    toolbar = NavigationToolbar2Tk(canvas, win)
                    toolbar.update()
                    canvas._tkcanvas.pack(fill=_tk.BOTH, expand=True)
                except Exception:
                    # toolbar is optional
                    pass
                return
        except Exception:
            # Not running inside Tk or embedding failed; fall back to show()
            pass

        plt.show()