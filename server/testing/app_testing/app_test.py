import pytest
from app import create_app, db
from models import User  # <-- import your model directly here

@pytest.fixture(scope='module')
def test_app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'supersecret',
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()

def test_signup_creates_user(test_client):
    response = test_client.post('/signup', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 201
    assert response.get_json()['message'] == "User created successfully"

    # Now query the user in the app context directly
    with test_client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.username == 'testuser'

def test_signup_fails_duplicate_username(test_client):
    # First signup
    test_client.post('/signup', json={'username': 'dupuser', 'password': 'pass1'})
    # Try duplicate
    response = test_client.post('/signup', json={'username': 'dupuser', 'password': 'pass2'})
    assert response.status_code == 409
    assert 'Username already taken' in response.get_json()['error']

def test_login_success(test_client):
    # Create user first
    test_client.post('/signup', json={'username': 'loginuser', 'password': 'mypassword'})
    response = test_client.post('/login', json={'username': 'loginuser', 'password': 'mypassword'})
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Login successful'

def test_login_fails_wrong_credentials(test_client):
    response = test_client.post('/login', json={'username': 'wronguser', 'password': 'wrongpass'})
    assert response.status_code == 401
    assert 'Invalid credentials' in response.get_json()['error']
