import unittest
import pandas as pd
from src.visualizer import Visualizer

class TestVisualizer(unittest.TestCase):

    def setUp(self):
        self.visualizer = Visualizer()
        self.test_data = {
            'Device': ['Device1', 'Device2'],
            'Value': [10, 20]
        }
        self.df = pd.DataFrame(self.test_data)

    def test_display_spreadsheet(self):
        # Test if the display_spreadsheet method works correctly
        try:
            self.visualizer.display_spreadsheet(self.df)
            result = True  # If no exception is raised, the test passes
        except Exception:
            result = False
        self.assertTrue(result)

    def test_display_graph(self):
        # Test if the display_graph method works correctly
        try:
            self.visualizer.display_graph(self.df)
            result = True  # If no exception is raised, the test passes
        except Exception:
            result = False
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()