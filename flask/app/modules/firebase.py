import pyrebase


class Firebase:
    def __init__(self):
        # Firebase configuration
        config = {
            "apiKey": "AIzaSyDvsdPFUgyr67aaXCtvignz0m8aM2ZdnTU",
            "authDomain": "paperreview-f9016.firebaseapp.com",
            "databaseURL": "",
            "projectId": "paperreview-f9016",
            "storageBucket": "paperreview-f9016.appspot.com",
            "messagingSenderId": "620720763534",
            "appId": "1:620720763534:web:d8aba558e4838cbdd84fdf",
            "measurementId": "G-1234567890",
        }
        self.firebase = pyrebase.initialize_app(config)
        self.storage = self.firebase.storage()

    def upload(self, file):
        self.storage.child("files/" + file).put(file)
        return self.storage.child("files/" + file).get_url(None)

    def download(self, url,path):
        self.storage.child("files/" + url).download(url,path)
