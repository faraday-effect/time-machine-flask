from flask import g
import psycopg2
import psycopg2.extras


class DbConnectionManager(object):
    def __init__(self, data_source_name):
        self.data_source_name = data_source_name
        self.is_open = False

    def open(self):
        if not self.is_open:
            g.connection = psycopg2.connect(self.data_source_name)
            g.cursor = g.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            self.is_open = True

    def close(self):
        if self.is_open:
            self.is_open = False
            g.cursor.close()
            g.connection.close()

    def is_open(self):
        return self.is_open


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
    INSERT INTO course(designation, name, semester_id)
    VALUES(%(designation)s, %(name)s, %(semester_id)s)
    """
    print(course_info)
    g.cursor.execute(query, course_info)
    g.connection.commit()
    return g.cursor.rowcount


def read_all_courses():
    query = """
SELECT
  course.id,
  course.designation, 
  course.name,
  format('%s %s', semester.name, semester.year) AS semester
FROM course
  INNER JOIN semester ON course.semester_id = semester.id
ORDER BY
  designation;
    """
    g.cursor.execute(query)
    return g.cursor.fetchall()


def read_all_semesters():
    g.cursor.execute("""
    SELECT
      id,
      format('%s %s', name, year) AS name
    FROM
      semester
    ORDER BY
      year, name
    """)
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
  semester.name AS semester_name,
  semester.year AS semester_year
FROM team
  INNER JOIN course ON team.course_id = course.id
  INNER JOIN semester ON course.semester_id = semester.id
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
