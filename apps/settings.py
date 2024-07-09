import sqlalchemy
import os

# when testing
# POSTGRES_DB_HOST = os.environ.get("POSTGRES_DB_HOST", "172.30.0.2")
POSTGRES_DB_HOST = os.environ.get("POSTGRES_DB_HOST", None)

SQLALCHEMY_DATABASE_URI = sqlalchemy.engine.url.URL.create(
    drivername="postgresql",
    username="postgres",
    password="postgres",
    host=POSTGRES_DB_HOST,
    port="5432",
    database="postgres",
)
# TODO: remove rubbish
if bool(int(os.environ.get("TESTING"))):
    JWT_SECRET_KEY = "secret1415@!kalm"
else:
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", None)