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

    # Email configuration - switches based on environment
    if env == 'production':
        # Gmail for productiongot
        MAIL_SERVER = 'smtp.gmail.com'
        MAIL_PORT = 465
        MAIL_USE_SSL = True
        MAIL_USERNAME = os.getenv('GMAIL_USERNAME')
        MAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
        MAIL_DEFAULT_SENDER = os.getenv('GMAIL_USERNAME')
    else:
        # Mailtrap for development/testing
        MAIL_SERVER = os.getenv('MAIL_SERVER', 'sandbox.smtp.mailtrap.io')
        MAIL_PORT = int(os.getenv('MAIL_PORT', 2525))
        MAIL_USE_TLS = True
        MAIL_USERNAME = os.getenv('MAIL_USERNAME')
        MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
        MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'test@fakeemail.com')
