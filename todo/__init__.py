from flask import Flask, render_template
from flaskext.mysql import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

from todo import routes