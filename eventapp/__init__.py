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
    from eventapp.booking import booking_bp
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(tasks)
    app.register_blueprint(booking_bp, url_prefix='/')

    #changed to main not admin because admi. initialized already exists

    @login_manager.user_loader
    def load_user(user_id):
        from eventapp.models import User
        return User.query.get(user_id)


def create_app(config_class=Config, check_and_send_reminders=None, clear_old_bookings=None):
    app = Flask(__name__)
    configure_app(app, config_class)
    configure_database(app)
    register_blueprints(app)

    scheduler.init_app(app)
    
    # Only add jobs if functions are provided
    if check_and_send_reminders is not None:
        scheduler.add_job(func=check_and_send_reminders, trigger='interval', args=[app], hours=1, id='email_reminder')
    
    if clear_old_bookings is not None:
        scheduler.add_job(func=clear_old_bookings, trigger='interval', args=[app], hours=24, id='clear_bookings')
    
    # Only start scheduler if it has jobs
    if scheduler.get_jobs():
        scheduler.start()
    app.config['PAYPAL_CLIENT_ID'] = os.getenv('PAYPAL_CLIENT_ID')
    app.config['PAYPAL_API_BASE'] = os.getenv('PAYPAL_API_BASE')

    from eventapp.admin import setup_admin
    setup_admin(app)



    return app


