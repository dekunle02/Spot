import copy
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class User:
    """id refers to the user's telegram id, signature_file_id also refers to telegram location of their signature"""
    id: str
    first_name: str
    last_name: str
    hospital_name: str
    signature_file_id: str

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'hospital_name': self.hospital_name,
            'signature_file_id': self.signature_file_id
        }

    @classmethod
    def from_dict(cls, obj_dict: dict):
        try:
            return User(
                id=obj_dict['id'],
                first_name=obj_dict['first_name'],
                last_name=obj_dict['last_name'],
                hospital_name=obj_dict['hospital_name'],
                signature_file_id=obj_dict['signature_file_id']
            )
        except Exception as e:
            print("Error: models.User fx: from_dict ", e)
            return None


@dataclass
class NightDisturbance:
    time: datetime
    duration: str
    reason: str

    def to_row(self) -> dict:
        return({
            "date": self.time.strftime("%d-%m-%Y"),
            "time":self.time.strftime("%H:%M"),
            "duration":self.duration,
            "reason":self.reason
        })


class TimeSheet:
    def __init__(self, user: User,  shift_start: datetime, shift_end: datetime) -> None:
        self.user = user
        self.shift_start = shift_start
        self.shift_end = shift_end
        self.night_disturbances = []

    def append_nightDisturbace(self, disturbance: NightDisturbance) -> None:
        self.night_disturbances.append(disturbance)

    def get_work_rows(self) -> list:
        work_rows = []
        start_time = copy.deepcopy(self.shift_start)
        last_time = copy.deepcopy(self.shift_end)
        midnight = start_time.replace(day=start_time.day+1, minute=0, hour=0, second=0, microsecond=0) 
        
        work_rows.append({
            "day" : start_time.strftime("%A"),
            "date": start_time.strftime("%d-%m-%Y"),
            "start_time":start_time.strftime("%H:%M"),
            "end_time":"00:00",
            "total_hours":self.get_hours_difference(start_time, midnight)
        })

        while midnight.date() < last_time.date():
            work_rows.append({
                "day" : midnight.strftime("%A"),
                "date": midnight.strftime("%d-%m-%Y"),
                "start_time": midnight.strftime("%H:%M"),
                "end_time":"00:00",
                "total_hours":24.0
            })
            midnight += timedelta(days=1)
        
        work_rows.append({
            "day" : last_time.strftime("%A"),
            "date": last_time.strftime("%d-%m-%Y"),
            "start_time":"00:00",
            "end_time":last_time.strftime("%H:%M"),
            "total_hours":self.get_hours_difference(midnight, last_time)
        })

        return work_rows

    def get_disturbance_rows(self) -> list:
        return [dist.to_row() for dist in self.night_disturbances] 

    def get_total_hours(self) -> float:
        return self.get_hours_difference(_from=self.shift_start, _to=self.shift_end)

    def get_hours_difference(self, _from: datetime, _to: datetime) -> float:
        delta: timedelta = _to - _from
        return round(delta.total_seconds()/3600, 2)
