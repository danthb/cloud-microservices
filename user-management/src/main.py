import datetime
import psycopg2
import hashlib
from fastapi import FastAPI, HTTPException
from database import get_db_connection
from models import UserRequest, UserResponse, UserAuth, UserAuthResponse, UserInfo


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("Starting up")
    print("Connecting to database for the first time")
    conn = get_db_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    try:
        print("Creating database")
        cursor.execute('CREATE DATABASE "users"')
    except psycopg2.DatabaseError as e:
        if e.pgcode != "42P04":
            raise e
        else:
            print("Database already exists")
    finally:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_ (
                "id" SERIAL PRIMARY KEY,
                "username" VARCHAR(255) NOT NULL,
                "email" VARCHAR(255) NOT NULL,
                "password" VARCHAR(255) NOT NULL,
                "salt" VARCHAR(255) NOT NULL,
                "token" VARCHAR(255),
                "created_at" TIMESTAMP NOT NULL,
                "expire_at" TIMESTAMP
            );
            """
        )
        conn.close()


@app.post("/users/", status_code=201)
async def create_user(user: UserRequest) -> UserResponse:
    if not user.username or not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Missing fields")
    conn = get_db_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM user_ WHERE username = %s OR email = %s;
        """,
        (user.username, user.email),
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="User already exists")
    salt = hashlib.sha256(user.password.encode()).hexdigest()
    created_date = datetime.datetime.now()
    cursor.execute(
        """
        INSERT INTO user_ (username, email, password, salt, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (user.username, user.email, user.password, salt, created_date),
    )
    user_id = cursor.fetchone()[0]
    conn.close()
    return UserResponse(id=user_id, created_at=created_date.strftime("%Y-%m-%d %H:%M:%S")[0:10])


@app.post("/users/auth/", status_code=200)
async def auth_user(user: UserAuth) -> UserAuthResponse:
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Missing fields")
    conn = get_db_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM user_ WHERE username = %s;
        """,
        (user.username,),
    )
    user_data = cursor.fetchone()
    if not user_data:
        raise HTTPException(status_code=400, detail="User does not exist")
    if user.password != user_data[3]:
        raise HTTPException(status_code=400, detail="User does not exist")
    token = hashlib.sha256(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode()).hexdigest()
    expire_date = datetime.datetime.now() + datetime.timedelta(minutes=5)
    cursor.execute(
        """
        UPDATE user_ SET token = %s, expire_at = %s WHERE id = %s;
        """,
        (token, expire_date, user_data[0]),
    )
    conn.close()
    return UserAuthResponse(id=user_data[0], token=token, expire_at=expire_date.strftime("%Y-%m-%d %H:%M:%S"))


@app.get("/users/me/", status_code=200)
async def get_user_info(token: str) -> UserInfo:
    if not token:
        raise HTTPException(status_code=400, detail="Missing fields")
    conn = get_db_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM user_ WHERE token = %s;
        """,
        (token,),
    )
    user_data = cursor.fetchone()
    if not user_data:
        raise HTTPException(status_code=400, detail="Token expired or invalid")
    if user_data[7] < datetime.datetime.now():
        raise HTTPException(status_code=400, detail="Token expired or invalid")
    conn.close()
    return UserInfo(id=user_data[0], username=user_data[1], email=user_data[2])


@app.get("/ping/", status_code=200)
async def ping() -> str:
    return "pong"

