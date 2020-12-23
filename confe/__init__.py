import os
from flask import Flask
from flask_login import LoginManager

UPLOAD_FOLDER = '~/confe/confe/instance'

app = Flask(__name__, instance_relative_config=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config.from_object('config.DevelopmentConfig')
app.config.from_pyfile('config.py')

login = LoginManager()
login.session_protection = 'strong'
login.login_view = 'login'
login.init_app(app)

import confe.views