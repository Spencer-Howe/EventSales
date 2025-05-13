import os
from dotenv import load_dotenv

class Config:
    # Load environment variables
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        load_dotenv('.env.production')
    else:
        load_dotenv('.env.local')
    SCHEDULER_API_ENABLED = True
    # App configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your_development_secret_key')
    PAYPAL_API_BASE = os.getenv('PAYPAL_API_BASE')

    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///yourdatabase.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('GMAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
