# firebase_init.py
import json
import base64
import os
import firebase_admin
from firebase_admin import credentials

if not firebase_admin._apps:
    b64 = os.environ.get('FIREBASE_CREDENTIALS_B64')
    if b64:
        decoded = base64.b64decode(b64).decode('utf-8')
        cred_dict = json.loads(decoded)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        print("⚠️ FIREBASE_CREDENTIALS_B64 no configurado — Firebase no se inicializó (probablemente entorno local)")