from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymongo
from sqlalchemy.orm import registry
from sqlalchemy.ext.automap import automap_base
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from server.config import Config

db = pymongo.MongoClient(Config.DATABASE_URI)
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from server.main.routes import main

    app.register_blueprint(main)

    return app
