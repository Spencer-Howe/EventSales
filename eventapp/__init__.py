from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()
admin = Admin()


def configure_database(app):
    db.init_app(app)
    migrate.init_app(app, db)


def configure_app(app, config_class=Config):
    app.config.from_object(config_class)
    login_manager.init_app(app)
    mail.init_app(app)
    admin.init_app(app)


def register_blueprints(app):
    from eventapp.views import views
    from eventapp.admin import admin_bp
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
#changed to main not admin because admi. initialized already exists


def create_app(config_class=Config):
    app = Flask(__name__)
    configure_app(app, config_class)
    configure_database(app)
    register_blueprints(app)

    #one of thes configs has to go
    app.config.from_pyfile('../config.py')
    @login_manager.user_loader
    def load_user(user_id):  # moved inside to provide clearer encapsulation
        from eventapp.models import User
        return User.query.get(int(user_id))




    return app
