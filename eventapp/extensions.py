from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()
admin = Admin(name='Admin', template_mode='bootstrap3')