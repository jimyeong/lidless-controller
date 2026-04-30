import os
from dotenv import load_dotenv

load_dotenv()

WRITE_DB_CONFIG = {
    "host": os.getenv("WRITE_DB_HOST"),
    "port": os.getenv("WRITE_DB_PORT"),
    "database": os.getenv("WRITE_DB_NAME"),
    "user": os.getenv("WRITE_DB_USER"),
    "password": os.getenv("WRITE_DB_PASSWORD"),
}

READ_DB_CONFIG = {
    "host": os.getenv("READ_DB_HOST"),
    "port": os.getenv("READ_DB_PORT"),
    "database": os.getenv("READ_DB_NAME"),
    "user": os.getenv("READ_DB_USER"),
    "password": os.getenv("READ_DB_PASSWORD"),
}