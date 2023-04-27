import os
import firebase_admin
from firebase_admin import credentials, storage, initialize_app

class Firebase():
    cred = None
    def __init__(self):
        # search credentials file in the same directory using os module
        self.cred = credentials.Certificate(os.path.dirname(__file__) + '/paperreview-f9016-ce492e6b99e4.json')
        initialize_app(self.cred, {'storageBucket': 'paperreview-f9016.appspot.com'})
        file = 'Dockerfile'
        bucket = storage.bucket() # Get a reference to the storage service, which is used to create buckets
        blob = bucket.blob(file) # Uploads a local file to the bucket
        blob.upload_from_filename(file)
