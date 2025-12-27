import unittest
from .utils import getTimeData
from datetime import datetime
from pathlib import Path

# Import your function here if it's in a different file
# from your_filename import getTimeData

class TestTimestampExtraction(unittest.TestCase):

    def test_standard_format(self):
        """Tests the YYYYMMDD_HHMMSS format."""
        filename = "IMG_20231025_123045.jpg"
        result = getTimeData(Path(filename))
        expected = datetime(2023, 10, 25, 12, 30, 45)
        self.assertEqual(result, expected)

    def test_epoch_format(self):
        """Tests the received_m_mid_... (Unix epoch) format."""
        filename = "received_m_mid_1410120397719_0cfa4cb619364e750.jpeg"
        result = getTimeData(Path(filename))
        # 1410120397 is Sunday, September 7, 2014 8:06:37 PM UTC
        # Note: result might vary slightly based on your local system timezone
        self.assertEqual(result.year, 2014)
        self.assertEqual(result.month, 9)
        self.assertEqual(result.day, 7)

    def test_no_match(self):
        """Tests that a filename with no date returns None."""
        filename = "vacation_photo.jpg"
        result = getTimeData(Path(filename))
        self.assertIsNone(result)

    def test_mixed_text(self):
        """Tests that it finds the pattern even with extra text around it."""
        filename = "backup_version_20220101_000000_final.zip"
        result = getTimeData(Path(filename))
        self.assertEqual(result, datetime(2022, 1, 1, 0, 0, 0))

if __name__ == '__main__':
    unittest.main()