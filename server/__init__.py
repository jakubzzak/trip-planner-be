from flask import Flask
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from server.config import Config

db = MongoEngine()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from server.main.routes import main
    from server.user.routes import users
    from server.trip.routes import trips
    from server.organization.routes import organizations
    from server.v1.routes import v1

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(trips)
    app.register_blueprint(organizations)
    app.register_blueprint(v1)

    return app
