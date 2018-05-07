from urllib.parse import urlparse, urljoin
from functools import wraps

from flask import Flask, render_template, flash, redirect, url_for, abort, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_debugtoolbar import DebugToolbarExtension

import pendulum
pendulum.set_formatter('alternative')

from user import User
from forms import LoginForm, SignupForm, DetailedTimeForm, CourseForm, ProjectForm, course_choices, TeamForm, \
    project_choices, team_choices, BulkTimeForm

import db

data_source_name = "dbname=time-machine user=tom host=localhost"
db_mgr = db.DbConnectionManager(data_source_name)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True

login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.debug = True
toolbar = DebugToolbarExtension(app)


@app.before_request
def before_request():
    db_mgr.open()


@app.teardown_request
def teardown_request(exception):
    db_mgr.close()


@login_manager.user_loader
def load_user(email):
    # Returns None if `email` is bogus.
    return User.read(email)


def account_access_ok(account_id):
    return current_user.is_superuser or current_user.id == account_id


def deny_access():
    flash("You don't have access to this function.")
    return redirect(url_for('index'))


# Based on http://flask.pocoo.org/snippets/98/
def superuser_required():
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.is_superuser:
                return f(*args, **kwargs)
            else:
                return deny_access()
        return wrapped
    return wrapper


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('time_sheet'))
    else:
        return redirect(url_for('login'))


# From http://flask.pocoo.org/snippets/62/
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https') and
            ref_url.netloc == test_url.netloc)


@app.route('/accounts/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.read(login_form.email.data)
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
    return render_template('accounts/login.html', form=login_form)


@app.route('/accounts/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/accounts/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm()
    signup_form.team_id.choices = team_choices()
    if signup_form.validate_on_submit():
        user = User.create(signup_form.first_name.data,
                           signup_form.last_name.data,
                           signup_form.email.data,
                           signup_form.password.data)
        if user is None:
            flash('Failed to create user')
        else:
            account = db.read_account_by_email(signup_form.email.data)
            default_role = db.read_default_role()
            row_count = db.create_account_team({'account_id': account['id'],
                                                'team_id': signup_form.team_id.data,
                                                'role_id': default_role['id']})
            if row_count == 1:
                flash('User {} created'.format(signup_form.email.data))
                return redirect(url_for('login'))
    return render_template('accounts/signup.html', form=signup_form)


@app.route('/accounts/all')
@login_required
@superuser_required()
def all_accounts():
    return render_template('accounts/all.html', accounts=db.read_all_accounts())


@app.route('/accounts/<int:account_id>')
@login_required
def account_details(account_id):
    if not account_access_ok(account_id):
        return deny_access()
    else:
        return render_template('accounts/details.html',
                               account=db.read_account_by_id(account_id),
                               teams=db.read_teams_by_account_id(account_id))


def combine_dates_times(time_entry):
    start_dt = pendulum.combine(time_entry['start_date'], time_entry['start_time'])
    stop_dt = pendulum.combine(time_entry['stop_date'], time_entry['stop_time'])
    return start_dt, stop_dt


def format_dates_times(start_dt, stop_dt):
    start_str = start_dt.format('MMM D h:mm A')
    stop_str = ''
    if start_dt.date() != stop_dt.date():
        stop_str += stop_dt.format(' MMM D')
    stop_str += stop_dt.format(' h:mm A')
    return start_str, stop_str


@app.route('/time-sheet')
@login_required
def time_sheet():
    entries = []
    total_duration = None
    for time_entry in db.read_time_entries(current_user.id):
        (start_dt, stop_dt) = combine_dates_times(time_entry)
        (start_str, stop_str) = format_dates_times(start_dt, stop_dt)
        duration = stop_dt - start_dt
        entries.append({ 'time_id': time_entry['time_id'],
                         'project_name': time_entry['project_name'],
                         'description': time_entry['description'],
                         'start_str': start_str,
                         'stop_str': stop_str,
                         'duration': duration})
        if total_duration is None:
            total_duration = duration
        else:
            total_duration += duration
    return render_template('time/sheet.html',
                           entries=entries,
                           total_duration=total_duration)


@app.route('/time-entry/bulk', methods=['GET', 'POST'])
@login_required
def enter_bulk_time():
    time_entry_form = BulkTimeForm()

    from pprint import pprint
    pprint(time_entry_form.data)

    # TODO: Refactor to eliminate redundancy with detailed time entry.
    choices = project_choices(current_user.id)
    if len(choices) < 1:
        flash('You are not assigned to any projects')
    time_entry_form.project_id.choices = choices

    if time_entry_form.validate_on_submit():
        pass
    return render_template('time/entry-bulk.html', form=time_entry_form)


@app.route('/time-entry/detailed', methods=['GET', 'POST'])
@login_required
def enter_detailed_time():
    time_entry_form = DetailedTimeForm()

    choices = project_choices(current_user.id)
    if len(choices) < 1:
        flash('You are not assigned to any projects')
    time_entry_form.project_id.choices = choices

    if time_entry_form.validate_on_submit():
        rowcount = db.create_time_entry({
            'project_id': time_entry_form.project_id.data,
            'user_id': current_user.id,
            'start_date': time_entry_form.start_date.data, 'start_time': time_entry_form.start_time.data,
            'stop_date': time_entry_form.stop_date.data, 'stop_time': time_entry_form.stop_time.data,
            'description': time_entry_form.desc.data
        })
        if rowcount == 1:
            flash("Added time successfully")
            return redirect(url_for('time_sheet'))
        else:
            flash("Problem adding time")
    return render_template('time/entry-detailed.html', form=time_entry_form)


@app.route('/time-entry/delete', methods=['POST'])
@login_required
def delete_time():
    time_id = request.form['time_id']
    row_count = db.delete_time_entry(time_id)
    if row_count == 1:
        return "OK"
    else:
        print("Failed to delete time {}".format(time_id))
        return "FAIL"


@app.route('/courses/all')
@login_required
@superuser_required()
def all_courses():
    return render_template('courses/all.html', courses=db.read_all_courses())


@app.route('/courses/create', methods=['GET', 'POST'])
@login_required
@superuser_required()
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


@app.route('/projects/create', methods=['GET', 'POST'])
@login_required
@superuser_required()
def create_project():
    project_form = ProjectForm()
    project_form.course_id.choices = course_choices()

    if project_form.validate_on_submit():
        rowcount = db.create_project({'name': project_form.name.data,
                                      'course_id': project_form.course_id.data})
        if rowcount == 1:
            flash('Project {} created'.format(project_form.name.data))
            return redirect(url_for('all_projects'))
    return render_template('projects/add.html', form=project_form)


@app.route('/projects/all')
@login_required
@superuser_required()
def all_projects():
    return render_template('projects/all.html', projects=db.read_all_projects())


@app.route('/teams/all')
@login_required
@superuser_required()
def all_teams():
    return render_template('teams/all.html', teams=db.read_all_teams())


@app.route('/teams/<int:team_id>')
@login_required
@superuser_required()
def team_details(team_id):
    return render_template('teams/details.html',
                           details=db.read_team_by_id(team_id),
                           members=db.read_members_by_team_id(team_id))


@app.route('/teams/create', methods=['GET', 'POST'])
@login_required
@superuser_required()
def create_team():
    team_form = TeamForm()
    team_form.course_id.choices = course_choices()
    team_form.project_id.choices = project_choices()

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
