from flask import g
import psycopg2
import psycopg2.extras

data_source_name = "dbname=time-machine user=tom host=localhost"


def open_db_connection():
    g.connection = psycopg2.connect(data_source_name)
    g.cursor = g.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


def close_db_connection():
    g.cursor.close()
    g.connection.close()


# User

def create_user(user):
    query = """
    INSERT INTO account (first_name, last_name, email, password_hash)
    VALUES (%(first)s, %(last)s, %(email)s, %(pass)s)
    """
    g.cursor.execute(query, {
        'first': user.first_name,
        'last': user.last_name,
        'email': user.email,
        'password_hash': user.password
    })
    g.connection.commit()
    return g.cursor.rowcount

def read_user_by_id(user_id):
    g.cursor.execute('SELECT * FROM account WHERE id = %(user_id)s', {'user_id': user_id})
    return g.cursor.fetchone()


def read_user_by_email(email):
    g.cursor.execute('SELECT * FROM account WHERE email = %(email)s', {'email': email})
    return g.cursor.fetchone()


def read_time_entries():
    g.cursor.execute('SELECT * FROM time ORDER BY start_date, start_time')
    return g.cursor.fetchall()


def create_time_entry(user_id, project_id, start_date, start_time, end_date, end_time, description):
    query = """
    INSERT INTO public.time (description, project_id, user_id, start_date, start_time, end_date, end_time)
    VALUES (%(desc)s, %(pid)s, %(uid)s, %(sd)s, %(st)s, %(ed)s, %(et)s)
    """
    g.cursor.execute(query, {
        'desc': description, 'pid': project_id, 'uid': user_id,
        'sd': start_date, 'st': start_time, 'ed': end_date, 'et': end_time
    })
    g.connection.commit()
    return g.cursor.rowcount
