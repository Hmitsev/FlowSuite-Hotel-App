import os
import streamlit as st
import psycopg2

def get_connection():

    database_url = os.getenv("LASTORIA_DATABASE_URL")

    st.error(database_url)

    return psycopg2.connect(database_url)
