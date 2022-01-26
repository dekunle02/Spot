import unittest
from datetime import datetime
from Spot.database.models import User, TimeSheet, NightDisturbance


class UserModelTest(unittest.TestCase):
    def test_user_converted_to_dict(self):
        """User can be converted into a dict object"""
        user = User(
            id='1',
            first_name="a",
            last_name= "b",
            hospital_name= "c",
            signature_file_id="d"
        )
        user_dict = user.to_dict()
        expected_dict = {
            'id': "1",
            'first_name': "a",
            'last_name': "b",
            'hospital_name': "c",
            'signature_file_id': "d"
        }

        self.assertEqual(user_dict, expected_dict)

class NightDisturbanceTestCase(unittest.TestCase):
    def test_night_disturbance_row_dict(self):
        """Night disturbance can be converted into dict row with time properly converted"""
        date_time = datetime.fromisoformat('2011-10-04 00:05:23.283')
        dist = NightDisturbance(
            time=date_time,
            duration='3min',
            reason="a"
        )
        expected_dict = {
            "date": "04-10-2011",
            "time": "00:05",
            "duration":"3min",
            "reason":"a"
        }
        self.assertEqual(dist.to_row(), expected_dict)

class TimeSheetTestCase(unittest.TestCase):
    
    def setUp(self) -> None:
        self.user = User(
             id='1',
            first_name="a",
            last_name= "b",
            hospital_name= "c",
            signature_file_id="d"
        )

        start = datetime.fromisoformat("2022-01-26 13:00:00.000")
        end = datetime.fromisoformat("2022-02-02 13:00:00.000")

        self.sheet = TimeSheet(
            user=self.user,
            shift_start=start,
            shift_end=end
        )

        return super().setUp()

    def test_night_dist_append(self):
        """Night disturbance can be appended to a timesheet"""
        date_time = datetime.fromisoformat('2011-10-04 00:05:23.283')
        dist = NightDisturbance(
            time=date_time,
            duration='3min',
            reason="a"
        )
        self.sheet.append_nightDisturbace(dist)
        
        self.assertEqual(dist, self.sheet.night_disturbances[0])

    def test_work_rows_created(self):
        """Work rows can be created from the timeSheet object"""
        work_rows = self.sheet.get_work_rows()
        expected_first_row =  {
            "day" : "Wednesday",
            "date": "26-01-2022",
            "start_time":"13:00",
            "end_time":"00:00",
            "total_hours":11.0
            }
        expected_second_row =  {
            "day" : "Thursday",
            "date": "27-01-2022",
            "start_time":"00:00",
            "end_time":"00:00",
            "total_hours":24.0
            }
        expected_last_row = {
            "day" : "Wednesday",
            "date": "02-02-2022",
            "start_time":"00:00",
            "end_time":"13:00",
            "total_hours":13.0
        }

        self.assertEqual(expected_first_row, work_rows[0])
        self.assertEqual(expected_second_row, work_rows[1])
        self.assertEqual(expected_last_row, work_rows[-1])
        self.assertEqual(len(work_rows), 8)

    def test_total_shift_time(self):
        """total time of shift calculated"""
        self.assertEqual(self.sheet.get_total_hours(), 168.0)
