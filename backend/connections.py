import os

import pika
from dotenv import load_dotenv
import psycopg2
from contextlib import contextmanager

load_dotenv()

RABBITMQ_URL = os.getenv('RABBITMQ_URL')
DATABASE_URL = os.getenv('DATABASE_URL')

print(f"Variables cargadas:  RABBITMQ_URL {os.getenv('DATABASE_URL')}" )
print(f"Variables cargadas:  DATABASE_URL {os.getenv('DATABASE_URL')}" )

@contextmanager
def get_rabbitmq_connection():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def get_postgres_connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()