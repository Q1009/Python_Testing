from tests.conftest import client

class TestLogout:

    def test_logout_redirects_to_homepage(self, client, login_as_valid_user):
        """Cas 1 — déconnexion : redirection vers la page d'accueil."""
        login_as_valid_user()
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b"Welcome to the GUDLFT Registration Portal!" in response.data

    def test_logout_clears_session(self, client, login_as_valid_user):
        """Cas 2 — déconnexion : la session est effacée."""
        login_as_valid_user()
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        with client.session_transaction() as session:
            assert 'club_email' not in session

    def test_logout_flash_message(self, client, login_as_valid_user):
        """Cas 3 — déconnexion : un message flash est affiché."""
        login_as_valid_user()
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b"You have been logged out." in response.data