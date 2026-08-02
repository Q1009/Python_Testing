# from tests.conftest import client
from urllib.parse import quote
from datetime import datetime, timedelta


class TestBooking:

    valid_club_name = "Simply Lift"
    valid_competition_name = "Fall Classic"
    invalid_club_name = "Invalid Club"
    invalid_competition_name = "Invalid Competition"

    def test_booking_with_valid_club_name_and_valid_competition_name(
            self, client, login_as_valid_user):
        """
        Case 1 — booking request with a valid club name
        and a valid competition name: access to the booking page.
        """
        login_as_valid_user()
        valid_club_name = quote(self.valid_club_name)
        valid_competition_name = quote(self.valid_competition_name)
        response = client.get(
            f'/book/{valid_competition_name}/{valid_club_name}',
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Booking for" in response.data

    def test_booking_with_invalid_club_name_and_valid_competition_name(
            self, client, login_as_valid_user):
        """
        Case 2 — booking request with an invalid club name
        and a valid competition name: redirect to the homepage
        with an error message.
        """
        login_as_valid_user()
        invalid_club_name = quote("Invalid Club")
        valid_competition_name = quote(self.valid_competition_name)
        response = client.get(
            f'/book/{valid_competition_name}/{invalid_club_name}',
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Summary | GUDLFT Registration" in response.data
        assert (
            b"Invalid booking URL. Please check the club name."
            in response.data
        )

    def test_booking_with_valid_club_name_and_invalid_competition_name(
            self, client, login_as_valid_user):
        """
        Case 3 — booking request with a valid club name
        and an invalid competition name: redirect to the homepage
        with an error message.
        """
        login_as_valid_user()
        invalid_competition_name = quote(self.invalid_competition_name)
        valid_club_name = quote(self.valid_club_name)
        response = client.get(
            f'/book/{invalid_competition_name}/{valid_club_name}',
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Summary | GUDLFT Registration" in response.data
        assert (
            b"Invalid booking URL. Please check the competition name."
            in response.data
        )

    def test_booking_with_invalid_club_name_and_invalid_competition_name(
            self, client, login_as_valid_user):
        """
        Case 4 — booking request with an invalid club name
        and an invalid competition name: redirect to the homepage
        with an error message.
        """
        login_as_valid_user()
        invalid_club_name = quote(self.invalid_club_name)
        invalid_competition_name = quote(self.invalid_competition_name)
        response = client.get(
            f'/book/{invalid_competition_name}/{invalid_club_name}',
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Summary | GUDLFT Registration" in response.data
        assert (
            b"Invalid booking URL. Please check the club name."
            in response.data
        )

    def test_booking_with_empty_club_name_and_valid_competition_name(
            self, client):
        """
        Case 5 — booking request with an empty club name and a
        valid competition name: redirect to the homepage with
        an error message.
        """
        invalid_club_name = quote("")
        valid_competition_name = quote(self.valid_competition_name)
        response = client.get(
            f'/book/{valid_competition_name}/{invalid_club_name}',
            follow_redirects=True,
        )
        assert response.status_code == 404

    def test_booking_with_valid_club_name_and_empty_competition_name(
            self, client):
        """
        Case 6 — booking request with a valid club name and an empty
        competition name: redirect to the homepage with an error message.
        """
        valid_club_name = quote(self.valid_club_name)
        invalid_competition_name = quote("")
        response = client.get(
            f'/book/{invalid_competition_name}/{valid_club_name}',
            follow_redirects=True,
        )
        assert response.status_code == 404

    def test_booking_with_empty_club_name_and_empty_competition_name(
            self, client):
        """
        Case 7 — booking request with an empty club name and an
        empty competition name: redirect to the homepage with
        an error message.
        """
        invalid_club_name = quote("")
        invalid_competition_name = quote("")
        response = client.get(
            f'/book/{invalid_competition_name}/{invalid_club_name}',
            follow_redirects=True,
        )
        assert response.status_code == 404

    def test_booking_with_past_competition_redirects_to_welcome(
            self, app, client, login_as_valid_user):
        """
        Case 8 — past competition: direct access to /book
        denied and return to welcome.
        """
        login_as_valid_user()
        app.config['COMPETITIONS'][0]['date'] = (
            datetime.now() - timedelta(days=1)
        ).strftime('%Y-%m-%d %H:%M:%S')

        valid_club_name = quote(self.valid_club_name)
        past_competition_name = quote(app.config['COMPETITIONS'][0]['name'])

        response = client.get(
            f'/book/{past_competition_name}/{valid_club_name}',
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Summary | GUDLFT Registration" in response.data
        assert (
            b"This competition is no longer open for booking."
            in response.data
        )

    def test_booking_requires_login(self, client):
        """Case 9 — user not logged in: redirect to index with message."""
        valid_club_name = quote(self.valid_club_name)
        valid_competition_name = quote(self.valid_competition_name)

        response = client.get(
            f'/book/{valid_competition_name}/{valid_club_name}',
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Please log in first." in response.data
        assert b"Welcome to the GUDLFT Registration Portal!" in response.data
