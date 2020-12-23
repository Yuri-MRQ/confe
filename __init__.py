import os
from flask import Flask
from flask_login import LoginManager

UPLOAD_FOLDER = '~/programacao/Flask/controles/confe/instance'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config.from_object('config.py')
app.config.from_envvar('YOURAPPLICATION_SETTINGS')

login = LoginManager()
login.session_protection = 'strong'
login.login_view = 'login'
login.init_app(app)