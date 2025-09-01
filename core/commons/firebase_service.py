
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from pyrebase import pyrebase

config = {
    "databaseURL": "",
    "apiKey": "AIzaSyAZCtA7GjMHZGQL7A0708K9bVke-nZ6SiE",
    "authDomain": "tine-fire.firebaseapp.com",
    "projectId": "tine-fire",
    "storageBucket": "tine-fire.appspot.com",
    "messagingSenderId": "831939331716",
    "appId": "1:831939331716:web:a6bae4f4e8eb8234ae64d1",
    "measurementId": "G-MZY1JDEMNQ"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()


def save_file(path_firebase: str, file: UploadedFile)-> str:
    default_storage.save(file.name, file)
    storage.child(path_firebase + file.name).put("media/" + file.name)
    default_storage.delete(file.name)
    return storage.child(path_firebase + file.name).get_url(token='')
