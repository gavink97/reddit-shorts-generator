from scripts.init_db import connect_to_database


def check_if_video_exists(db_user, db_pass, db_host, db_port, db_database, submission_id, top_comment_id):
    db = connect_to_database(db_user, db_pass, db_host, db_port)
    cursor = db.cursor()

    use_database = f"USE {db_database};"
    cursor.execute(use_database)

    videos_query = """
        SELECT * FROM uploads
        WHERE submission_id = %s
        AND top_comment_id = %s;
        """

    cursor.execute(videos_query, (submission_id, top_comment_id))
    rows = cursor.fetchall()

    if len(rows) > 0:
        video_exists = True
        print("video found in DB")

    else:
        video_exists = False
        print("video not in DB")

    db.commit()
    cursor.close()
    db.close()

    return video_exists


def write_to_db(db_user, db_pass, db_host, db_port, db_database, submission_id, top_comment_id):
    db = connect_to_database(db_user, db_pass, db_host, db_port)
    cursor = db.cursor()

    use_database = f"USE {db_database};"
    cursor.execute(use_database)

    write_to_videos = """
    INSERT INTO uploads (submission_id, top_comment_id)
    VALUES (%s, %s);
    """

    cursor.execute(write_to_videos, (submission_id, top_comment_id))
    db.commit()

    print("Updated DB")

    cursor.close()
    db.close()
