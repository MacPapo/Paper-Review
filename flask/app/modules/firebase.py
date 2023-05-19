import pyrebase
from config import FIREBASE_CONFIG


class Firebase:
    def __init__(self):
        self.firebase = None
        self.storage = None

    def init_app(self, app):
        self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        self.storage = self.firebase.storage()

    def upload(self, file):
        self.storage.child("files/" + file).put(file)
        return self.storage.child("files/" + file).get_url(None)

    def download(self, url, file):
        self.storage.child("files/" + url).download(file)
