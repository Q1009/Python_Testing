

class TestLogout:

    def test_logout_redirects_to_homepage(self, client, login_as_valid_user):
        """Case 1 — logout: redirects to the homepage."""
        login_as_valid_user()
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b"Welcome to the GUDLFT Registration Portal!" in response.data

    def test_logout_clears_session(self, client, login_as_valid_user):
        """Case 2 — logout: the session is cleared."""
        login_as_valid_user()
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        with client.session_transaction() as session:
            assert 'club_email' not in session

    def test_logout_flash_message(self, client, login_as_valid_user):
        """Case 3 — logout: a flash message is displayed."""
        login_as_valid_user()
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b"You have been logged out." in response.data
