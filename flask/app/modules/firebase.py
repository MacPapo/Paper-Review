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

<<<<<<< HEAD
    def download(self, url, file):
        self.storage.child("files/" + url).download(file)
=======
    def download(self, name):
        remove_extension = lambda n: n[:-24]
        dest = (
            self.download_directory
            + remove_extension(name)
            + datetime.datetime.now().strftime("-%Y-%m-%d-%H-%M-%S")
            + ".pdf"
        )
        self.storage.child(
            self.firebase_directory + self.upload_directory + name
        ).download(path=self.download_directory, filename=dest)
        return "/" + dest
>>>>>>> f2c6ff9fe98284cdc62dc40c20ab547a71a495d5
