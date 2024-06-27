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
    from eventapp.admin import admin1, setup_admin
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(admin1, url_prefix='/admin')




    #changed to main not admin because admi. initialized already exists
    @login_manager.user_loader
    def load_user(userid):
        from eventapp.models import User
        return User.query.filter(User.id == userid).first()


def create_app(config_class=Config):
    app = Flask(__name__)
    configure_app(app, config_class)
    configure_database(app)
    register_blueprints(app)




    return app


