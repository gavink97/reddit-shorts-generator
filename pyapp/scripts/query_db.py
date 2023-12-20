import mysql.connector
import os
import pandas as pd
import requests
import time
import logging
from dotenv import load_dotenv
from config import launcher_path


load_dotenv()
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_database = os.environ['MYSQL_DB']

db = mysql.connector.connect(
    user=f'{db_user}',
    password=f'{db_pass}',
    host=f'{db_host}',
    port=f'{db_port}',
    database=f'{db_database}'
)


def check_if_video_exists():
    pass


def write_video_to_db():
    pass
