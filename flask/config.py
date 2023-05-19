# config.py


# API configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyDvsdPFUgyr67aaXCtvignz0m8aM2ZdnTU",
    "authDomain": "paperreview-f9016.firebaseapp.com",
    "databaseURL": "",
    "projectId": "paperreview-f9016",
    "storageBucket": "paperreview-f9016.appspot.com",
    "messagingSenderId": "620720763534",
    "appId": "1:620720763534:web:d8aba558e4838cbdd84fdf",
    "measurementId": "G-1234567890",
}


class Config:
    # Flask configuration
    SECRET_KEY = "bucami"

    # File upload configuration
    ALLOWED_EXTENSIONS = ["pdf"]

    # Database configuration
    SQLALCHEMY_DATABASE_URI = "postgresql://moonphase:eclipse@db:5432/paper_review"
