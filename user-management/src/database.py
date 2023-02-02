import psycopg2
from time import sleep
import os
from typing import Optional
from models import UserBase, UserRequest, UserResponse, UserAuth, UserAuthResponse, UserInfo


class User(UserBase): pass
class UserReq(UserRequest): pass
class UserRes(UserResponse): pass
class UserAuthReq(UserAuth): pass
class UserAuthRes(UserAuthResponse): pass
class UserInfoRes(UserInfo): pass


def _get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("USER_DATABASE_HOST"),
        database="users",
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )
    return conn


def get_db_connection():
    attempts = 0
    while True:
        attempts += 1
        try:
            return _get_db_connection()
        except psycopg2.OperationalError as e:
            print("Could not connect to database, trying again")
            sleep(3)
            if attempts > 5:
                print("Could not connect to database, giving up")
                raise e
