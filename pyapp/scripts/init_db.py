import mysql.connector
import os
import time
from dotenv import load_dotenv

load_dotenv()
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']


def connect_to_database(db_user, db_pass, db_host, db_port):
    global db
    max_retries = 5
    retries = 0

    while retries < max_retries:
        try:
            db = mysql.connector.connect(
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
            )
            return db
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            retries += 1
            if retries < max_retries:
                print("Retrying in 5 seconds...")
                time.sleep(10)
            else:
                print("Max retry attempts reached. Unable to connect to the database.")
                raise


def create_tables():
    cursor = db.cursor()

    use_database = "USE videos"

    create_uploads_table = """
    CREATE TABLE IF NOT EXISTS uploads (
        id INT AUTO_INCREMENT PRIMARY KEY,
        submission_author VARCHAR(255),
        submission_title VARCHAR(900),
        submission_timestamp INT,
        top_comment_author VARCHAR(255),
        top_comment_body VARCHAR(900)
    )
    """

    cursor.execute(use_database)
    cursor.execute(create_uploads_table)
    db.commit()
    cursor.close()
    db.close()


connect_to_database(db_user, db_pass, db_host, db_port)
create_tables()
print("Tables created")
