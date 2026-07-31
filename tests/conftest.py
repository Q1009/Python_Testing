import pytest
import multiprocessing as mp
from contextlib import contextmanager
from flask import session
from server import create_app


# LiveServerTestCase uses multiprocessing; on macOS/Python 3.13, spawn can fail
# to pickle Flask-Testing's local worker function. Prefer fork for test runs.
try:
    mp.set_start_method("fork")
except RuntimeError:
    # Start method already set by the test runner/interpreter.
    pass
except ValueError:
    # Fallback for platforms where fork is unavailable.
    pass


@pytest.fixture
def app(mock_clubs, mock_competitions):
    return create_app(
        {"TESTING": True},
        clubs=mock_clubs,
        competitions=mock_competitions,
    )


@pytest.fixture
def client(app):
    """Flask test client with testing mode enabled."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def login_as_valid_user(client):
    def _login(email='john@simplylift.co'):
        return client.post(
            '/show_summary',
            data={'email': email},
            follow_redirects=True,
        )

    return _login


@pytest.fixture
def mock_clubs():
    return [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"},
        {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"},
    ]


@pytest.fixture
def mock_competitions():
    return [
        {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "number_of_places": "25"},
        {"name": "Fall Classic", "date": "2026-10-22 13:30:00", "number_of_places": "13"},
    ]


@pytest.fixture
def request_session(app):
    @contextmanager
    def _request_session(club_email=None):
        with app.test_request_context('/'):
            if club_email is not None:
                session['club_email'] = club_email
            yield

    return _request_session