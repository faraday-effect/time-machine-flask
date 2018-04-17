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


def read_user_by_email(email):
    query = """
    SELECT
      account.id AS account_id,
      first_name, last_name, email, password_hash,
      role_id, role.name  AS role_name
    FROM account
    INNER JOIN account_role ON account.id = account_role.account_id
    INNER JOIN role ON account_role.role_id = role.id
    WHERE email = %(email)s
    """
    g.cursor.execute(query, {'email': email})
    return g.cursor.fetchone()


# Course

def create_course(course_info):
    query = """
    INSERT INTO course(designation, name, semester, year)
    VALUES(%(designation)s, %(name)s, %(semester)s, %(year)s)
    """
    g.cursor.execute(query, course_info)
    g.connection.commit()
    return g.cursor.rowcount


def read_all_courses():
    g.cursor.execute('SELECT * FROM course ORDER BY designation')
    return g.cursor.fetchall()


# Team


def create_team(team_info):
    query = """
    INSERT INTO team(name, course_id)
    VALUES(%(name)s, %(course_id)s)
    """
    g.cursor.execute(query, team_info)
    g.connection.commit()
    return g.cursor.rowcount


def read_all_teams():
    query = """
SELECT
  team.id     AS team_id,
  team.name   AS team_name,
  course.id   AS course_id,
  designation,
  course.name AS course_name,
  semester,
  year
FROM team
  INNER JOIN course ON team.course_id = course.id
ORDER BY
  team_name, designation;
    """
    g.cursor.execute(query)
    return g.cursor.fetchall()


# Time

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
