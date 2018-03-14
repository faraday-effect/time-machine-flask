from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import Email, Length, DataRequired, NumberRange, InputRequired, EqualTo

import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'


@app.before_request
def before_request():
    db.open_db_connection()


@app.teardown_request
def teardown_request(exception):
    db.close_db_connection()


@app.route('/')
def index():
    return render_template('index.html')


class SignInForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password')
    submit = SubmitField('Sign In')



@app.route('/sign-in')
def sign_in():
    sign_in_form = SignInForm()
    return render_template('sign-in.html', form=sign_in_form)


@app.route('/time-sheet')
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


if __name__ == '__main__':
    app.run(debug=True)