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
def create_account(user_info):
    query = """
        INSERT INTO account (first_name, last_name, email, password_hash)
        VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password_hash)s)
        RETURNING *
    """
    g.cursor.execute(query, user_info)
    g.connection.commit()
    return g.cursor.fetchone()


def create_account_team(account_team_info):
    query = """
        INSERT INTO account_team(account_id, team_id, role_id) 
        VALUES (%(account_id)s, %(team_id)s, %(role_id)s) 
    """
    g.cursor.execute(query, account_team_info)
    g.connection.commit()
    return g.cursor.rowcount


def read_all_accounts():
    query = """
        SELECT
          account.id           AS account_id,
          first_name,
          last_name,
          email,
          superuser,
          account_team.team_id AS team_id,
          team.name            AS team_name,
          project.id           AS project_id,
          project.name         AS project_name,
          account_team.role_id AS role_id,
          role.name            AS role_name
        FROM account
          LEFT OUTER JOIN account_team ON account.id = account_team.account_id
          LEFT OUTER JOIN team ON account_team.team_id = team.id
          LEFT OUTER JOIN role ON account_team.role_id = role.id
          LEFT OUTER JOIN project ON team.project_id = project.id
        ORDER BY last_name, first_name;
    """
    g.cursor.execute(query)
    return g.cursor.fetchall()


def read_default_role():
    g.cursor.execute('SELECT * FROM role WHERE is_default')
    rows = g.cursor.fetchall()
    if len(rows) != 1:
        raise Exception('Got {} rows for default role'.format(len(rows)))
    return rows[0]


def read_account_by_email(email):
    query = """
        SELECT *
        FROM account
        WHERE email = %(email)s
    """
    g.cursor.execute(query, {'email': email})
    return g.cursor.fetchone()


# Project
def create_project(project_info):
    query = """
        INSERT INTO project(name, course_id)
        VALUES (%(name)s, %(course_id)s)
    """
    g.cursor.execute(query, project_info)
    g.connection.commit()
    return g.cursor.rowcount


def read_all_projects():
    query = """
        SELECT
          project.id         AS project_id,
          project.name       AS project_name,
          course.id          AS course_id,
          course.designation AS course_designation,
          course.name                                   AS course_name,
          format('%s %s', semester.name, semester.year) AS semester
        FROM project
          INNER JOIN course ON project.course_id = course.id
          INNER JOIN semester ON course.semester_id = semester.id
        ORDER BY
          semester DESC, course.designation ASC, project_name ASC
    """
    g.cursor.execute(query)
    return g.cursor.fetchall()


# Course
def create_course(course_info):
    query = """
        INSERT INTO course(designation, name, semester_id)
        VALUES(%(designation)s, %(name)s, %(semester_id)s)
    """
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
        INSERT INTO team(name, course_id, project_id)
        VALUES(%(name)s, %(course_id)s, %(project_id)s)
    """
    g.cursor.execute(query, team_info)
    g.connection.commit()
    return g.cursor.rowcount


def read_all_teams():
    query = """
        SELECT
          team.id            AS team_id,
          team.name          AS team_name,
          course.id          AS course_id,
          course.designation AS course_designation,
          course.name        AS course_name,
          format('%s %s', semester.name, semester.year)
                             AS semester,
          project.id         AS project_id,
          project.name       AS project_name
        FROM team
          INNER JOIN course ON team.course_id = course.id
          INNER JOIN semester ON course.semester_id = semester.id
          INNER JOIN project ON team.project_id = project.id
        ORDER BY
          team_name, designation
    """
    g.cursor.execute(query)
    return g.cursor.fetchall()


# Time
def read_time_entries(account_id=None):
    """Read time entries for the given account or all entries (default)"""
    base_query = """
        SELECT
          time.id      AS time_id,
          account_id,
          description,
          start_date,
          start_time,
          end_date,
          end_time,
          project.id   AS project_id,
          project.name AS project_name
        FROM time
          INNER JOIN project ON time.project_id = project.id
    """
    if account_id is None:
        g.cursor.execute(base_query)
    else:
        query = base_query + "WHERE account_id = %(account_id)s"
        g.cursor.execute(query, {'account_id': account_id})
    return g.cursor.fetchall()


def create_time_entry(time_entry_info):
    query = """
        INSERT INTO public.time (description, project_id, account_id, 
          start_date, start_time, 
          end_date, end_time)
        VALUES (%(description)s, %(project_id)s, %(user_id)s, 
          %(start_date)s, %(start_time)s, 
          %(end_date)s, %(end_time)s)
    """
    g.cursor.execute(query, time_entry_info)
    g.connection.commit()
    return g.cursor.rowcount
