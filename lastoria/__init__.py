import os

import psycopg2


def get_connection():
    database_url = os.getenv("LASTORIA_DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "Липсва LASTORIA_DATABASE_URL в Environment настройките на Render."
        )

    return psycopg2.connect(database_url)
