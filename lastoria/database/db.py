import os

import psycopg2


def get_connection():
    database_url = os.getenv("LASTORIA_DATABASE_URL")

    print("LASTORIA URL =", database_url)

    return psycopg2.connect(database_url)
