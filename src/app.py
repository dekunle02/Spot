import utils
from datetime import datetime
from database import models

t = models.TimeSheet(
    user=models.User(
        id="1",
        first_name="a",
        last_name="b",
        hospital_name="c",
        signature_file_id="AgACAgQAAxkBAAIBBGHzPvXzYTCRvtn4kHAZOCrCSBgVAALntTEb98WZUxgTkUZfB6RuAQADAgADeAADIwQ",
    ),
    shift_start=datetime.fromisoformat("2022-01-26 13:00:00.000"),
    shift_end=datetime.fromisoformat("2022-02-02 13:00:00.000"),
)

res = utils.make_html(t, write_to_file=False)
print(res)
