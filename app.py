from urllib.parse import urlparse, urljoin
import datetime

from flask import Flask, render_template, flash, redirect, url_for, abort, request
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import SubmitField, StringField, PasswordField, HiddenField, SelectField
from wtforms.fields.html5 import DateField, TimeField, IntegerField
from wtforms.validators import Email, Length, DataRequired, NumberRange, InputRequired, EqualTo

data_source_name = "dbname=time-machine user=tom host=localhost"

import db

db_mgr = db.DbConnectionManager(data_source_name)
from user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.before_request
def before_request():
    db_mgr.open()


@app.teardown_request
def teardown_request(exception):
    db_mgr.close()


@login_manager.user_loader
def load_user(email):
    user = User().read(email)
    if user.valid_user:
        return user
    else:
        return None


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('time_sheet'))
    else:
        return redirect(url_for('login'))


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password')
    next = HiddenField('Next')
    submit = SubmitField('Sign In')


# From http://flask.pocoo.org/snippets/62/
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https') and
            ref_url.netloc == test_url.netloc)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User().read(login_form.email.data)
        if user is not None:
            if user.verify_password(login_form.password.data):
                login_user(user)
                flash('Logged in successfully')
                next = request.args.get('next')
                if not is_safe_url(next):
                    return abort(400)
                return redirect(next or url_for('index'))
            else:
                flash('Login failed')
    return render_template('login.html', form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/settings')
@login_required
def settings():
    return "ZOWIE"


@app.route('/time-sheet')
@login_required
def time_sheet():
    return render_template('time-sheet.html', entries=db.read_time_entries())


class TimeEntryForm(FlaskForm):
    start_date = DateField('Start Date')
    start_time = TimeField('Start Time')
    end_date = DateField('End Date')
    end_time = TimeField('End Time')
    description = StringField('Description')
    submit = SubmitField('Add Time Entry')


@app.route('/time-entry', methods=['GET', 'POST'])
@login_required
def time_entry():
    time_entry_form = TimeEntryForm()
    if time_entry_form.validate_on_submit():
        rowcount = db.create_time_entry(1, 1,
                                        time_entry_form.start_date.data,
                                        time_entry_form.start_time.data,
                                        time_entry_form.end_date.data,
                                        time_entry_form.end_time.data,
                                        time_entry_form.description.data)
        if rowcount == 1:
            flash("Added time successfully")
            return redirect(url_for('time_sheet'))
        else:
            flash("Problem adding time")
    return render_template('time-entry.html', form=time_entry_form)


class CourseForm(FlaskForm):
    designation = StringField('Designation',
                              render_kw={'placeholder': '(e.g., SYS394)'},
                              validators=[InputRequired()])
    name = StringField('Course Name',
                       render_kw={'placeholder': '(e.g., Information Systems Design)'},
                       validators=[InputRequired()])
    semester_id = SelectField('Semester', coerce=int)
    submit = SubmitField()


@app.route('/courses/all')
@login_required
def all_courses():
    return render_template('courses/all.html', courses=db.read_all_courses())


@app.route('/courses/create', methods=['GET', 'POST'])
@login_required
def create_course():
    course_form = CourseForm()
    course_form.semester_id.choices = [(row['id'], row['name']) for row in db.read_all_semesters()]

    if course_form.validate_on_submit():
        rowcount = db.create_course({'designation': course_form.designation.data,
                                     'name': course_form.name.data,
                                     'semester_id': course_form.semester_id.data})
        if rowcount == 1:
            flash('Course {} created'.format(course_form.name.data))
            return redirect(url_for('all_courses'))
    return render_template('courses/add.html', form=course_form)


class ProjectForm(FlaskForm):
    name = StringField('Project Name',
                       render_kw={'placeholder': '(e.g., Home Church Manager)'},
                       validators=[InputRequired()])
    course_id = SelectField('Course', coerce=int)
    submit = SubmitField()


@app.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    project_form = ProjectForm()
    project_form.course_id.choices = [(row['id'],
                                       Markup("{}&mdash;{} ({})".format(row['designation'],
                                                                        row['name'],
                                                                        row['semester'])))
                                      for row in db.read_all_courses()]

    if project_form.validate_on_submit():
        rowcount = db.create_project({'name': project_form.name.data,
                                      'course_id': project_form.course_id.data})
        if rowcount == 1:
            flash('Project {} created'.format(project_form.name.data))
            return redirect(url_for('all_projects'))
    return render_template('projects/add.html', form=project_form)


@app.route('/projects/all')
@login_required
def all_projects():
    return render_template('projects/all.html', projects=db.read_all_projects())


@app.route('/teams/all')
@login_required
def all_teams():
    return render_template('teams/all.html', teams=db.read_all_teams())


class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[InputRequired()])
    course_id = SelectField('Course', coerce=int)
    project_id = SelectField('Project', coerce=int)
    submit = SubmitField()


@app.route('/teams/create', methods=['GET', 'POST'])
@login_required
def create_team():
    team_form = TeamForm()
    team_form.course_id.choices = [(row['id'],
                                    "{}-{} ({})".format(row['designation'],
                                                        row['name'],
                                                        row['semester']))
                                   for row in db.read_all_courses()]
    team_form.project_id.choices = [(row['project_id'], row['project_name'])
                                    for row in db.read_all_projects()]

    if team_form.validate_on_submit():
        rowcount = db.create_team({'name': team_form.name.data,
                                   'course_id': team_form.course_id.data,
                                   'project_id': team_form.project_id.data})
        if rowcount == 1:
            flash('Team {} created'.format(team_form.name.data))
            return redirect(url_for('all_teams'))
    return render_template('teams/add.html', form=team_form)


if __name__ == '__main__':
    app.run(debug=True)
