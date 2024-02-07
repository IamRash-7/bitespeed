from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_URL, SQLALCHEMY_TRACK_MODIFICATIONS
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from src.routes import api_blueprint
app.register_blueprint(api_blueprint)