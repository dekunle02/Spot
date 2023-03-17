import os
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

from .models import User


load_dotenv()
FIREBASE_KEY_DIR = Path(__file__).parents[0]/ 'firebase_key.json'
DATABASE_URL =  os.environ['FIREBASE_URL']
USER_PATH = '/users/'

credentials = credentials.Certificate(FIREBASE_KEY_DIR)
firebase_admin.initialize_app(credentials)


db_ref = db.reference(url=DATABASE_URL, path=USER_PATH)

def add_user(user: User) -> None:
    db_ref.push().set(value=user.to_dict())

def get_user_with_id(id: str) -> User:
    user = None
    try:
        for key, value in db_ref.get().items():
            if value['id'] == id:
                user = User.from_dict(value)
                return user
    except:
        return user    
            
def get_all_users():
    user_list = []
    try:
        for key,value in db_ref.get().items():
            user_list.append(User.from_dict(value))
    except:
        return user_list 
    

def update_user(id: str, **kwargs):
    try:
        for key,value in db_ref.get().items():
            if value['id'] == id:
                db_ref.child(key).update(kwargs)
                return
    except:
        return


def delete_user(id: str):
    try:
        for key,value in db_ref.get().items():
            if value['id'] == id:
                db_ref.child(key).delete()
    except:
        return
