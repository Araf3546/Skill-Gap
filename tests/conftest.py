"""
Shared pytest fixtures using a per-test in-memory SQLite database.
"""
import pytest

from app import create_app
from src.database.models import db as _db


@pytest.fixture
def app():
    flask_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        },
        create_tables=False,
    )

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()