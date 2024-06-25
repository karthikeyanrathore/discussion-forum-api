import sqlalchemy
import os

POSTGRES_DB_HOST = os.environ.get("POSTGRES_DB_HOST", "172.30.0.2")

SQLALCHEMY_DATABASE_URI = sqlalchemy.engine.url.URL.create(
    drivername="postgresql",
    username="postgres",
    password="postgres",
    host=POSTGRES_DB_HOST,
    port="5432",
    database="postgres",
)
# TODO: remove rubbish
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "asdkasvdkvaskdg")