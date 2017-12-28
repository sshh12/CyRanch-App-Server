import urlparse
import os

from cfisdapi import app

LOCAL = False # Running Locally = W/O Database

try:
    # If the VAR exists this probably is attach to a database
    url = urlparse.urlparse(os.environ["DATABASE_URL"])
    urlparse.uses_netloc.append("postgres")

    import psycopg2

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cur = conn.cursor()

except Exception as e:

    print("Running Locally b/c " + str(e))
    LOCAL = True


def set_grade(user, subject, name, grade, gradetype):

    if not LOCAL:

        try:

            cur.execute("SELECT 1 FROM grades WHERE user_id=%s AND name=%s AND subject=%s;", [user, name, subject])
            if cur.fetchone() == None:
                cur.execute("INSERT INTO grades (user_id, name, subject, grade, gradetype) values (%s,%s,%s,%s,%s);",
                            [user, name, subject, grade, gradetype])
            else:
                cur.execute("UPDATE grades SET grade=%s, gradetype=%s WHERE user_id=%s AND name=%s AND subject=%s;",
                            [grade, gradetype, user, name, subject])
            conn.commit()
            return True

        except Exception as e:
            print("grade db error - " + str(e))
            conn.rollback()

    return False

def is_user(user):

    if not LOCAL:

        cur.execute("SELECT 1 FROM demo WHERE user_id=%s;", [user])
        return fetchone() != None

    return False

def add_user(user, demo):

    if not LOCAL:

        try:
            cur.execute("INSERT INTO demo (user_id, name, school, language, gender, gradelevel) values (%s,%s,%s,%s,%s,%s);",
                        [user, demo['name'], demo['school'], demo['language'], demo['gender'], demo['gradelevel']])
            conn.commit()

            return True

        except Exception as e:
            print("add db error - " + str(e))
            conn.rollback()

    return False

def add_rank(user, transcript):

    if not LOCAL:

        try:

            cur.execute("SELECT 1 FROM rank WHERE user_id=%s;", [user])
            if cur.fetchone() == None:
                cur.execute("INSERT INTO rank (user_id, gpa, pos, classsize) values (%s,%s,%s,%s);",
                            [user, transcript['gpa']['value'], transcript['gpa']['rank'], transcript['gpa']['class_size']])
            else:
                cur.execute("UPDATE rank SET pos=%s, classsize=%s, gpa=%s WHERE user_id=%s;",
                            [transcript['gpa']['rank'], transcript['gpa']['class_size'], transcript['gpa']['value'], user])
            conn.commit()

            return True

        except Exception as e:
            print("transcript db error - " + str(e))
            conn.rollback()

    return False

def add_news(picture, organization, eventdate, text, link, type_, check=False):

    if not LOCAL:

        try:

            if check: # Check if event already exists

                cur.execute("select 1 from news where description=%s and organization=%s",
                            [text, organization])

                if cur.fetchone() != None:
                    return False

            cur.execute("insert into news (picture, organization, eventdate, description, link, contenttype) values (%s,%s,%s,%s,%s,%s);",
                        [picture, organization, eventdate, text, link, type_])

            conn.commit()
            return True

        except Exception as e:
            print("news db error - " + str(e))
            conn.rollback()

    return False

def get_news():

    if not LOCAL:

        if cur.execute("select * from news"):

            for news in cur.fetchall():

                yield news

def get_news_orgs():

    if not LOCAL:

        cur.execute('select distinct organization from news')

        for org in cur.fetchall():

            yield org[0]

# Proxies for interacting with `cur` database object

def execute(*args):
    if not LOCAL:
        cur.execute(*args)
        return True
    else:
        return None


def fetchone():
    if not LOCAL:
        return cur.fetchone()
    else:
        return []


def fetchall():
    if not LOCAL:
        return cur.fetchall()
    else:
        return []
