# conftest.py (or inside your test file)
import pytest
from app import create_app
from models import db

@pytest.fixture(scope='module')
def test_client():
    test_config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True
    }
    flask_app = create_app(test_config)

    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()
