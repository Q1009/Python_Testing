from tests.conftest import client

class TestLogin:

    def test_login_with_valid_email(self, client):
        """Case 1 — login with a valid email: access to the dashboard."""
        response = client.post(
            '/show_summary',
        data={'email': 'john@simplylift.co'},
        follow_redirects=True,
    )
        assert response.status_code == 200
        assert b"Welcome" in response.data

    def test_login_with_invalid_email(self, client):
        """Case 2 — login with an invalid email: error message displayed."""
        response = client.post(
            '/show_summary',
        data={'email': 'invalid_email@example.com'},
        follow_redirects=True,
    )
        assert response.status_code == 200
        assert b"Unfortunately, the email you entered was not found." in response.data

    def test_login_with_empty_email(self, client):
        """Case 3 — login with an empty email: error message displayed."""
        response = client.post(
            '/show_summary',
        data={'email': ''},
        follow_redirects=True,
    )
        assert response.status_code == 200
        assert b"Unfortunately, the email you entered was not found." in response.data

    def test_login_with_white_space_email(self, client):
        """Case 4 — login with an email containing spaces: access granted."""
        response = client.post(
            '/show_summary',
            data={'email': '  john@simplylift.co  '},
        follow_redirects=True,
    )
        assert response.status_code == 200
        assert b"Welcome" in response.data

    def test_login_with_case_insensitive_email(self, client):
        """Case 5 — login with a different case email: access granted."""
        response = client.post(
            '/show_summary',
            data={'email': 'JOHN@SIMPLYLIFT.CO'},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Welcome" in response.data


    def test_login_with_special_characters_email(self, client):
        """Case 6 — login with an email containing special characters: error message displayed."""
        response = client.post(
            '/show_summary',
        data={'email': 'john@simplylift.co!'},
        follow_redirects=True,
    )
        assert response.status_code == 200
        assert b"Unfortunately, the email you entered was not found." in response.data
