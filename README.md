# Dataset Organizer

This project is designed to organize and visualize datasets collected from various devices using LoRaWAN technology. It provides functionalities to load, clean, and organize data, as well as visualize it in either spreadsheet or graph format.

## Project Structure

```
dataset-organizer
├── src
│   ├── main.py            # Entry point of the application
│   ├── organizer.py       # Contains the Organizer class for data processing
│   ├── visualizer.py      # Contains the Visualizer class for data visualization
│   ├── devices.py         # Contains device-related constants and functions
│   └── utils.py           # Utility functions for data processing and visualization
├── data
│   ├── raw
│   │   └── sample_device_1.csv  # Raw data for a sample device
│   └── processed
│       └── device_1_clean.csv    # Cleaned and organized data for device 1
├── notebooks
│   └── explore.ipynb      # Jupyter notebook for exploratory data analysis
├── tests
│   ├── test_organizer.py   # Unit tests for the Organizer class
│   └── test_visualizer.py  # Unit tests for the Visualizer class
├── requirements.txt        # Project dependencies
├── .gitignore              # Files and directories to ignore in version control
└── README.md               # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd dataset-organizer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python src/main.py
   ```

2. Follow the prompts to load and visualize your dataset.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.