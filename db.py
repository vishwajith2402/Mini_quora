import os

import mysql.connector


def get_connection():
    host = os.getenv("MINI_QUORA_DB_HOST", "localhost")
    user = os.getenv("MINI_QUORA_DB_USER", "root")
    password = os.getenv("MINI_QUORA_DB_PASSWORD", "")
    database = os.getenv("MINI_QUORA_DB_NAME", "mini_quora")

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
    )
