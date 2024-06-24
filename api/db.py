from flask import Flask
from pymongo import MongoClient


def init_db(app: Flask):
    client = MongoClient(app.config["MONGODB_URI"])
    app.db = client["mydatabase"]
