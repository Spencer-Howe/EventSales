import pytest
from eventapp import create_app

@pytest.fixture
def app():
    """Create Flask app using your existing configuration"""
    app = create_app()
    app.config['TESTING'] = True
    # Disable scheduler for testing
    if hasattr(app, 'scheduler'):
        app.scheduler.shutdown()
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()