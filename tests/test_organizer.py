import unittest
import pandas as pd
from src.organizer import Organizer

class TestOrganizer(unittest.TestCase):

    def setUp(self):
        self.organizer = Organizer()
        self.raw_data_path = 'data/raw/sample_device_1.csv'
        self.processed_data_path = 'data/processed/device_1_clean.csv'

    def test_load_data(self):
        data = self.organizer.load_data(self.raw_data_path)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)

    def test_clean_data(self):
        data = self.organizer.load_data(self.raw_data_path)
        cleaned_data = self.organizer.clean_data(data)
        self.assertIsInstance(cleaned_data, pd.DataFrame)
        self.assertFalse(cleaned_data.empty)

    def test_organize_by_device(self):
        data = self.organizer.load_data(self.raw_data_path)
        organized_data = self.organizer.organize_by_device(data)
        self.assertIsInstance(organized_data, pd.DataFrame)
        self.assertTrue('Device' in organized_data.columns)

    def test_save_processed_data(self):
        data = self.organizer.load_data(self.raw_data_path)
        cleaned_data = self.organizer.clean_data(data)
        self.organizer.save_processed_data(cleaned_data, self.processed_data_path)
        processed_data = pd.read_csv(self.processed_data_path)
        self.assertEqual(cleaned_data.shape[0], processed_data.shape[0])

if __name__ == '__main__':
    unittest.main()