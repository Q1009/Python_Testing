class TestPointsBoard:

    def test_points_board_is_publicly_accessible(self, client):
        response = client.get('/pointsBoard', follow_redirects=True)

        assert response.status_code == 200
        assert b"Public Points Board" in response.data
        assert b"Back to Login" in response.data

    def test_points_board_is_accessible_after_login(self, client, login_as_valid_user):
        login_as_valid_user()
        response = client.get('/pointsBoard', follow_redirects=True)

        assert response.status_code == 200
        assert b"Public Points Board" in response.data
        assert b"Logout" in response.data

    def test_points_board_displays_club_names_and_points(self, client):
        response = client.get('/pointsBoard', follow_redirects=True)

        assert response.status_code == 200
        assert b"Simply Lift" in response.data
        assert b"13" in response.data
        assert b"Iron Temple" in response.data
        assert b"4" in response.data
        assert b"She Lifts" in response.data
        assert b"12" in response.data

    def test_points_board_is_updated_after_booking(self, client, login_as_valid_user):
        # Simulate a booking to change the points of a club
        login_as_valid_user()
        response1 = client.post(
            '/purchasePlaces',
            data={
                'competition': 'Fall Classic',
                'places': '3',
            },
            follow_redirects=True,
        )
        assert response1.status_code == 200

        # Now check the points board to see if the points have been updated
        response2 = client.get('/pointsBoard', follow_redirects=True)

        assert response2.status_code == 200
        assert b"Simply Lift" in response2.data
        assert b"10" in response2.data  # Points should be updated from 13 to 10 after booking 3 places
