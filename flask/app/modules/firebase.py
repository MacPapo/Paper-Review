import os
import firebase_admin
from firebase_admin import credentials, storage, initialize_app
from cryptography.fernet import Fernet


class Firebase:
    def __init__(self):
        self.cred = credentials.Certificate(
            os.path.dirname(__file__) + "/paperreview-f9016-ce492e6b99e4.json"
        )
        initialize_app(self.cred, {"storageBucket": "paperreview-f9016.appspot.com"})

    def crypt(self, key, message):
        f = Fernet(key)
        token = f.encrypt(message.encode())
        return token

    def decrypt(self, key, token):
        f = Fernet(key)
        message = f.decrypt(token)
        return message.decode()

    def upload(self, file):
        bucket = storage.bucket()
        blob = bucket.blob(file)
        blob.upload_from_filename(file)
        key = Fernet.generate_key()
        return (key, self.crypt(key, blob.public_url))
