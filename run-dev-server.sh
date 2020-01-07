#!/usr/bin/env bash

source ./venv/bin/activate

FLASK_APP=app.py
FLASK_ENV=develoment

flask run
