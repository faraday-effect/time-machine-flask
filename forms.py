from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import SubmitField, StringField, PasswordField, HiddenField, SelectField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import Email, InputRequired, EqualTo

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
    email = StringField('Email', validators=[Email()])
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


class TimeEntryForm(FlaskForm):
    start_date = DateField('Start Date')
    start_time = TimeField('Start Time')
    end_date = DateField('End Date')
    end_time = TimeField('End Time')
    description = StringField('Description')
    submit = SubmitField('Add Time Entry')


def course_choices():
    return [(row['id'],
             Markup("{}&mdash;{} ({})".format(row['designation'], row['name'], row['semester'])))
             for row in db.read_all_courses()]


def project_choices():
    return [(row['project_id'], row['project_name'])
            for row in db.read_all_projects()]


def team_choices():
    return [(row['team_id'], row['team_name'])
            for row in db.read_all_teams()]
