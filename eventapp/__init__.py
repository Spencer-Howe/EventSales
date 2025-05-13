import os

from flask import Flask
from config import Config
from .extensions import db, migrate, mail, login_manager, scheduler


def configure_database(app):
    db.init_app(app)
    migrate.init_app(app, db)


def configure_app(app, config_class=Config):
    app.config.from_object(config_class)
    login_manager.init_app(app)
    mail.init_app(app)


def register_blueprints(app):
    from eventapp.views import views
    from eventapp.tasks import tasks
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(tasks)

    #changed to main not admin because admi. initialized already exists

    @login_manager.user_loader
    def load_user(user_id):
        from eventapp.models import User
        return User.query.get(user_id)


def create_app(config_class=Config, scheduler=None, check_and_send_reminders=None):
    app = Flask(__name__)
    configure_app(app, config_class)
    configure_database(app)
    register_blueprints(app)

    scheduler.init_app(app)
    scheduler.add_job(func=check_and_send_reminders, trigger='interval', hours=1, id='email_reminder')
    scheduler.start()
    app.config['PAYPAL_CLIENT_ID'] = os.getenv('PAYPAL_CLIENT_ID')
    app.config['PAYPAL_API_BASE'] = os.getenv('PAYPAL_API_BASE')

    from eventapp.admin import setup_admin
    setup_admin(app)



    return app


