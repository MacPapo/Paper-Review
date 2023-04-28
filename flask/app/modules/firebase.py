import os
import firebase_admin
from firebase_admin import credentials, storage as fs
from google.cloud import storage
from google.oauth2 import service_account
from app.modules.crypt import Crypt


class Firebase:
    def __init__(self):
        self.cred = credentials.Certificate(
            os.path.dirname(__file__) + "/paperreview-f9016-ce492e6b99e4.json"
        )  # get credentials
        self.fire = firebase_admin.initialize_app(
            self.cred, {"storageBucket": "paperreview-f9016.appspot.com"}
        )  # initialize firebase
        self.gcloud = storage.Client(
            credentials=service_account.Credentials.from_service_account_file(
                os.path.dirname(__file__) + "/paperreview-f9016-ce492e6b99e4.json"
            )
        )  # initialize gcloud
        self.bucket = self.gcloud.bucket(fs.bucket().name)

    def upload(self, file):
        crypt = Crypt()
        blob = self.bucket.blob(file)
        blob.upload_from_filename(file)
        key = crypt.generate_key
        # generate a blob url
        # https://cloud.google.com/storage/docs/access-public-data#api-link
        return (key, crypt.encrypt(key, blob.public_url))

    def retrive(self, key, url):
        return self.gcloud.list_blobs(
            self.bucket.name
        )  # fetch all the files in the bucket

    def upload_blob(self, source_file_name, destination_blob_name):
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
