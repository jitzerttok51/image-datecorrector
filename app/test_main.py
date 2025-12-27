import unittest
from .utils import getTimeData
from datetime import datetime
from pathlib import Path

# Import your function here if it's in a different file
# from your_filename import getTimeData

import unittest
from pathlib import Path
from datetime import datetime

class TestTimestampExtraction(unittest.TestCase):

    def test_standard_format(self):
        """Tests the YYYYMMDD_HHMMSS and Screenshot formats."""
        # Standard underscore
        self.assertEqual(getTimeData(Path("20150124_211718.mp4")), datetime(2015, 1, 24, 21, 17, 18))
        # Screenshot with dash
        self.assertEqual(getTimeData(Path("Screenshot_20171103-020935.png")), datetime(2017, 11, 3, 2, 9, 35))

    def test_dashed_dot_format(self):
        """Tests 'YYYY-MM-DD HH.MM.SS' with Cyrillic suffixes."""
        filename = "2014-07-22 20.27.07-редактирано.jpg"
        expected = datetime(2014, 7, 22, 20, 27, 7)
        self.assertEqual(getTimeData(Path(filename)), expected)

    def test_whatsapp_format(self):
        """Tests the 'IMG-YYYYMMDD-WA' format."""
        filename = "IMG-20130426-WA0001.jpg"
        expected = datetime(2013, 4, 26, 0, 0, 0)
        self.assertEqual(getTimeData(Path(filename)), expected)

    def test_epoch_formats(self):
        """Tests various Epoch formats (FB, Messenger, IMG-ms)."""
        samples = [
            "FB_IMG_1446114923469.jpg",
            "received_m_mid_1410120397719_0cfa4cb619364e750.jpeg",
            "IMG-1419336966300-V-редактирано.jpg"
        ]
        for s in samples:
            result = getTimeData(Path(s))
            self.assertIsNotNone(result, f"Failed to parse {s}")
            # Checking year ensures epoch conversion worked
            self.assertIn(result.year, [2014, 2015]) 

    def test_action_cam_file_format(self):
        """Tests the 'FILEYYMMDD-HHMMSS' format."""
        filename = "FILE180215-171034-004212.MP4"
        expected = datetime(2018, 2, 15, 17, 10, 34)
        self.assertEqual(getTimeData(Path(filename)), expected)

    def test_collage_and_edits(self):
        """Tests patterns followed by '-COLLAGE' or Cyrillic 'редактирано'."""
        self.assertEqual(
            getTimeData(Path("20171010_174718-COLLAGE-редактирано.jpg")), 
            datetime(2017, 10, 10, 17, 47, 18)
        )

    # def test_long_numeric_img(self):
    #     """Tests the long string 'IMG_YYMMDDHHMMSS...'."""
    #     filename = "IMG_180830270710386.jpeg"
    #     # Assuming 18-08-30 27:07:10 (though 27 hours is invalid, 
    #     # let's assume the parser handles valid YYMMDDHHMMSS)
    #     result = getTimeData(Path(filename))
    #     if result:
    #         self.assertEqual(result.year, 2018)
    #         self.assertEqual(result.month, 8)

    def test_no_match(self):
        """Tests that a filename with no date returns None."""
        self.assertIsNone(getTimeData(Path("vacation_photo.jpg")))

if __name__ == '__main__':
    unittest.main()