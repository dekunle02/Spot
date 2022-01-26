import os
import firebase_admin
from firebase_admin import credentials, db

from dotenv import load_dotenv
load_dotenv()

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

DATABASE_URL =  os.environ['FIREBASE_URL']
