import os
import firebase_admin
from firebase_admin import credentials, storage, initialize_app
from google.cloud import storage as gcs
from google.oauth2 import service_account
from cryptography.fernet import Fernet


class Firebase:
    def __init__(self):
        self.cred = credentials.Certificate(
            os.path.dirname(__file__) + "/paperreview-f9016-ce492e6b99e4.json"
        )  # get credentials
        self.fire = initialize_app(
            self.cred, {"storageBucket": "paperreview-f9016.appspot.com"}
        )  # initialize firebase
        self.bucket = storage.bucket(app=self.fire)  # get bucket

    def crypt(self, key, message):
        f = Fernet(key)
        token = f.encrypt(
            message.encode()
        )  # Encrypt the bytes. The returning object is of type bytes
        return token

    def decrypt(self, key, token):
        f = Fernet(key)
        message = f.decrypt(token)
        return message.decode()

    def upload(self, file):
        blob = self.bucket.blob(file)
        blob.upload_from_filename(file)
        key = Fernet.generate_key()
        # generate a blob url
        # https://cloud.google.com/storage/docs/access-public-data#api-link
        return (key, self.crypt(key, blob.public_url))

    def retrive(self, key, url):
        files = storage.Client(credentials=self.cred).list_blobs(
            self.bucket().name
        )  # fetch all the files in the bucket
        return files

    def upload_blob(bucket_name, source_file_name, destination_blob_name):
        credentials = service_account.Credentials.from_service_account_file(
             os.path.dirname(__file__) + "/paperreview-f9016-ce492e6b99e4.json"
        )
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    upload_blob(
        firebase_admin.storage.bucket().name,
        "uploads/keepme.txt",
        "images/keepme.txt",
    )
