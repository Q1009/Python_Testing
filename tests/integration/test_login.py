from tests.conftest import client

class TestLogin:

    def test_login_with_valid_email(self, client):
        """Cas 1 — connexion avec un email valide : accès à l'accueil."""
        response = client.post(
            '/showSummary',
        data={'email': 'john@simplylift.co'},
        follow_redirects=True,
    )
        assert response.status_code == 200
        assert b"Welcome" in response.data

    def test_login_with_invalid_email(self, client):
        """Cas 2 — connexion avec un email invalide : message d'erreur affiché."""
        response = client.post(
            '/showSummary',
        data={'email': 'invalid_email@example.com'},
        follow_redirects=True,
    )
        assert response.status_code == 200
        assert b"Unfortunately, the email you entered was not found." in response.data

    def test_login_with_empty_email(self, client):
        """Cas 3 — connexion avec un email vide : message d'erreur affiché."""
        response = client.post(
            '/showSummary',
        data={'email': ''},
        follow_redirects=True,
    )
        assert response.status_code == 200
        assert b"Unfortunately, the email you entered was not found." in response.data

    def test_login_with_whitespace_email(self, client):
        """Cas 4 — connexion avec un email contenant des espaces : accès autorisé."""
        response = client.post(
            '/showSummary',
            data={'email': '  john@simplylift.co  '},
        follow_redirects=True,
    )
        assert response.status_code == 200
        assert b"Welcome" in response.data

    def test_login_with_case_insensitive_email(self, client):
        """Cas 5 — connexion avec un email de casse différente : accès autorisé."""
        response = client.post(
            '/showSummary',
            data={'email': 'JOHN@SIMPLYLIFT.CO'},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Welcome" in response.data


    def test_login_with_special_characters_email(self, client):
        """Cas 6 — connexion avec un email contenant des caractères spéciaux : message d'erreur affiché."""
        response = client.post(
            '/showSummary',
        data={'email': 'john@simplylift.co!'},
        follow_redirects=True,
    )
        assert response.status_code == 200
        assert b"Unfortunately, the email you entered was not found." in response.data
