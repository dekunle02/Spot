import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

from .models import User, TimeSheet, NightDisturbance


load_dotenv()
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"

if DEVELOPMENT_MODE:
    print("fire development mode")
else:
    print("fire prod mode")

MY_TELEGRAM_ID = os.getenv("MY_TELEGRAM_ID")
FIREBASE_KEY_DIR = Path(__file__).parents[0] / "firebase_key.json"
DATABASE_URL = os.environ["FIREBASE_URL"]
USER_PATH = "/users/"

credentials = credentials.Certificate(FIREBASE_KEY_DIR)
firebase_admin.initialize_app(credentials)


db_ref = db.reference(url=DATABASE_URL, path=USER_PATH)


def add_user(user: User) -> None:
    db_ref.push().set(value=user.to_dict())


def get_user_with_id(id: str) -> User:
    user = None
    try:
        for key, value in db_ref.get().items():
            if value["id"] == id:
                user = User.from_dict(value)
                return user
    except Exception as e:
        print("Exception:", e)
        return user


def get_all_users():
    user_list = []
    if DEVELOPMENT_MODE:
        print("developement mode get all user")
        return [
            User(
                first_name="Abdulsamad",
                last_name="Adeleke",
                id=MY_TELEGRAM_ID,
                hospital_name="Nuffield Taunton",
                signature_file_id="AgACAgQAAxkBAAIGcmH2prlnxU87Qv7n_IcYi8EwgVHqAAIOtjEbECGwU9DWmdd5FsA6AQADAgADeAADIwQ",
            )
        ]
    try:
        user_pairs = list(db_ref.order_by_key().get().items())
        # print("user_pairs::", user_pairs)
        for i, value in user_pairs:
            user = User.from_dict(value)
            user_list.append(user)
        return user_list
    except Exception as e:
        print("exception:", e)
        return user_list


def update_user(id: str, **kwargs):
    try:
        for key, value in db_ref.get().items():
            if value["id"] == id:
                db_ref.child(key).update(kwargs)
                return
    except:
        return


def delete_user(id: str):
    try:
        for key, value in db_ref.get().items():
            if value["id"] == id:
                db_ref.child(key).delete()
    except:
        return


def supply_fake_timesheet():
    user = User(
        first_name="Abdulsamad",
        last_name="Adeleke",
        id=MY_TELEGRAM_ID,
        hospital_name="Nuffield Taunton",
        signature_file_id="AgACAgQAAxkBAAIGcmH2prlnxU87Qv7n_IcYi8EwgVHqAAIOtjEbECGwU9DWmdd5FsA6AQADAgADeAADIwQ",
    )

    start = datetime.fromisoformat("2022-01-26 13:00:00.000")
    end = datetime.fromisoformat("2022-02-02 13:00:00.000")

    timesheet = TimeSheet(user=user, shift_start=start, shift_end=end)

    timesheet.append_nightDisturbance(
        NightDisturbance(time=start, duration="3min", reason="a")
    )
    timesheet.append_nightDisturbance(
        NightDisturbance(time=end, duration="4min", reason="b")
    )
    return timesheet
