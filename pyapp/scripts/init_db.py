import mysql.connector
import time


def connect_to_database(db_user, db_pass, db_host, db_port):
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


def test_db_connection(db_user, db_pass, db_host, db_port, db_database):
    max_retries = 5
    retries = 0

    while retries < max_retries:
        try:
            db = mysql.connector.connect(
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                database=db_database
            )
            print(f"Connection to {db_database} Successful")
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

    db.close()


def create_tables(db_user, db_pass, db_host, db_port, db_database):
    db = connect_to_database(db_user, db_pass, db_host, db_port)
    cursor = db.cursor()

    use_database = f"USE {db_database};"
    cursor.execute(use_database)

    create_uploads_table = """
    CREATE TABLE IF NOT EXISTS uploads (
        id INT AUTO_INCREMENT PRIMARY KEY,
        submission_id VARCHAR(30),
        top_comment_id VARCHAR(30)
    );
    """

    cursor.execute(create_uploads_table)
    db.commit()

    cursor.close()
    db.close()
