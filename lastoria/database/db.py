import streamlit as st
import os
import psycopg2

def get_connection():

    database_url = os.getenv("LASTORIA_DATABASE_URL")

    st.error(
        database_url[:120]
    )

    return psycopg2.connect(database_url)
