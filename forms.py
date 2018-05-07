from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import SubmitField, StringField, PasswordField, HiddenField, SelectField, FieldList, FormField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import Email, InputRequired, EqualTo, Optional, Regexp

import db


class CourseForm(FlaskForm):
    designation = StringField('Designation',
                              render_kw={'placeholder': '(e.g., SYS394)'},
                              validators=[InputRequired()])
    name = StringField('Course Name',
                       render_kw={'placeholder': '(e.g., Information Systems Design)'},
                       validators=[InputRequired()])
    semester_id = SelectField('Semester', coerce=int)
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password')
    next = HiddenField('Next')
    submit = SubmitField('Sign In')


class ProjectForm(FlaskForm):
    name = StringField('Project Name',
                       render_kw={'placeholder': '(e.g., Home Church Manager)'},
                       validators=[InputRequired()])
    course_id = SelectField('Course', coerce=int)
    submit = SubmitField()


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    team_id = SelectField('Team', coerce=int)
    password = PasswordField('Password', validators=[InputRequired()])
    password_repeat = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')


class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[InputRequired()])
    course_id = SelectField('Course', coerce=int)
    project_id = SelectField('Project', coerce=int)
    submit = SubmitField()


# I wanted to call the `desc` field `description`, but that appears to cause problems with the `FieldList`
# because `description` is a named parameter of the underlying `Field` constructor.
class DetailedTimeForm(FlaskForm):
    project_id = SelectField('Project', coerce=int)
    start_date = DateField('Start Date')
    start_time = TimeField('Start Time')
    stop_date = DateField('Stop Date')
    stop_time = TimeField('Stop Time')
    desc = StringField('Description')
    submit = SubmitField('Add Time Entry')


class BulkTimeEntry(FlaskForm):
    date = DateField('Date', validators=[Optional()])
    duration = StringField('Duration',
                           render_kw={'placeholder': 'HH:MM'},
                           validators=[Optional(), Regexp(r'\d{1,2}:\d{2}')])
    desc = StringField('Description')


class BulkTimeForm(FlaskForm):
    project_id = SelectField('Project', coerce=int)
    entries = FieldList(FormField(BulkTimeEntry), min_entries=5)
    submit = SubmitField('Add All Entries')


def course_choices():
    return [(row['id'],
             Markup("{}&mdash;{} ({})".format(row['designation'], row['name'], row['semester'])))
            for row in db.read_all_courses()]


def project_choices(account_id):
    return [(row['project_id'],
             "{} ({})".format(row['project_name'], row['role_name']))
            for row in db.read_projects_by_account_id(account_id)]


def team_choices():
    return [(row['team_id'], row['team_name'])
            for row in db.read_all_teams()]
