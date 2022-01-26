import os

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

from .models import User


load_dotenv()
credentials = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(credentials)

DATABASE_URL =  os.environ['FIREBASE_URL']
USER_PATH = '/users/'

db_ref = db.reference(url=DATABASE_URL, path=USER_PATH)


def add_user(user: User) -> None:
    db_ref.push.set(value=user.to_dict())

def get_user_with_id(id: str) -> User:
    user = None
    for key, value in db_ref.get().items():
        if value['id'] == id:
            user = User.from_dict(value)
            break
    return user
            
def get_all_users():
    user_list = []
    for key,value in db_ref.get().items():
        user_list.append(User.from_dict(value))

def update_user(id: str, **kwargs):
   for key,value in db_ref.get().items():
       if value['id'] == id:
           db_ref.child(key).update(kwargs)
           return

def delete_user(id: str):
    for key,value in db_ref.get().items():
       if value['id'] == id:
           db_ref.child(key).delete()
           