from datetime import datetime, timedelta

def cap_each_word(string: str) -> str:
    words = string.split(" ")
    return (" ".join([word.capitalize() for word in words])).strip()

def convert_string_into_date(date_string: str, time_string: str) -> datetime:
    """Expected date:05-12-2021 time:04:30"""
    string_format = "%d-%m-%Y %H:%M"
    try:
        return datetime.strptime(f"{date_string} {time_string}",format=string_format)
    except:
        return None

def get_end_datetime_from_with_time(start_date: datetime, days: int, time: str) -> datetime:
        try:
            end_date = start_date + timedelta(days=days)
            hour, minute = time.split(":")
            end_date = end_date.replace(hour=int(hour), minute=int(minute))
            return end_date
        except:
            return None

