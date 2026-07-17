import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "d0e1c8da1a14fc3f219c0fc778d979c5b40bd4c41bc29611"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "banco.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
