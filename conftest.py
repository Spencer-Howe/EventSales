import pytest
import tempfile
import os
from eventapp import create_app
from eventapp.extensions import db
from eventapp.models import User, Customer, Event, Booking, Payment, Waiver

@pytest.fixture
def app():
    """Create Flask app with test configuration"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Disable scheduler for testing
    if hasattr(app, 'scheduler'):
        try:
            app.scheduler.shutdown()
        except:
            pass
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        yield db.session

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    user = User(username='testuser', password='testpass123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_customer(db_session):
    """Create a sample customer for testing"""
    customer = Customer(
        name='John Doe',
        email='john.doe@example.com',
        phone='555-1234'
    )
    db_session.add(customer)
    db_session.commit()
    return customer

@pytest.fixture
def sample_event(db_session, sample_user):
    """Create a sample event for testing"""
    from datetime import datetime, timedelta
    event = Event(
        title='Halloween Test Event',
        start=datetime.now() + timedelta(days=7),
        end=datetime.now() + timedelta(days=7, hours=2),
        description='Test event description',
        price_per_ticket=35.0,
        max_capacity=50,
        user_id=sample_user.id
    )
    db_session.add(event)
    db_session.commit()
    return event