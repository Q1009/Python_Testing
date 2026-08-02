import json
from datetime import datetime
from unittest.mock import mock_open, patch
from utils import (
    load_clubs,
    load_competitions,
    get_club_by_email,
    lower_case_email,
    strip_white_space,
    get_competition_by_name,
    get_club_by_name,
    get_club_points,
    get_competition_places,
    is_competition_bookable,
    is_booking_valid,
    update_club_points,
    update_competition_places,
    get_booking_key,
    get_logged_club,
)


class TestLoadClubs:

    def test_returns_all_clubs(self, mock_clubs):
        """Case 1 — valid file with multiple clubs: returns all elements."""
        data = json.dumps({"clubs": mock_clubs})
        with patch("builtins.open", mock_open(read_data=data)):
            result = load_clubs()
        assert len(result) == 3

    def test_each_club_has_required_keys(self, mock_clubs):
        """Case 2 — each club contains the name, email, and points keys."""
        data = json.dumps({"clubs": mock_clubs})
        with patch("builtins.open", mock_open(read_data=data)):
            result = load_clubs()
        for club in result:
            assert "name" in club
            assert "email" in club
            assert "points" in club

    def test_returns_single_club(self):
        """
        Case 3 — valid file with a single club:
        Returns a list with one element.
        """
        club = [{"name": "Simply Lift",
                 "email": "john@simplylift.co", "points": "13"}]
        data = json.dumps({"clubs": club})
        with patch("builtins.open", mock_open(read_data=data)):
            result = load_clubs()
        assert len(result) == 1
        assert result[0]["name"] == "Simply Lift"

    def test_returns_empty_list_when_clubs_is_empty(self):
        """Case 4 — 'clubs' key present but empty list: returns []."""
        data = json.dumps({"clubs": []})
        with patch("builtins.open", mock_open(read_data=data)):
            result = load_clubs()
        assert result == []

    def test_raises_file_not_found_when_file_missing(self):
        """Case 5 — file not found: returns None."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert load_clubs() is None

    def test_raises_json_decode_error_on_invalid_json(self):
        """Case 6 — invalid JSON content: returns None."""
        with patch("builtins.open", mock_open(read_data="not valid json {")):
            assert load_clubs() is None

    def test_raises_key_error_when_clubs_key_missing(self):
        """Case 7 — 'clubs' key missing from JSON: returns None."""
        data = json.dumps({"wrong_key": []})
        with patch("builtins.open", mock_open(read_data=data)):
            assert load_clubs() is None


class TestLoadCompetitions:

    def test_returns_all_competitions(self, mock_competitions):
        """
        Case 1 — valid file with multiple competitions:
        Returns all elements.
        """
        data = json.dumps({"competitions": mock_competitions})
        with patch("builtins.open", mock_open(read_data=data)):
            result = load_competitions()
        assert len(result) == 2

    def test_each_competition_has_required_keys(self, mock_competitions):
        """
        Case 2 — each competition contains the name,
        date, and number_of_places keys.
        """
        data = json.dumps({"competitions": mock_competitions})
        with patch("builtins.open", mock_open(read_data=data)):
            result = load_competitions()
        for competition in result:
            assert "name" in competition
            assert "date" in competition
            assert "number_of_places" in competition

    def test_returns_single_competition(self):
        """
        Case 3 — valid file with a single competition:
        Returns a list with one element.
        """
        competition = [
            {
                "name": "Spring Festival",
                "date": "2025-03-27 10:00:00",
                "number_of_places": "25"
            }
        ]
        data = json.dumps({"competitions": competition})
        with patch("builtins.open", mock_open(read_data=data)):
            result = load_competitions()
        assert len(result) == 1
        assert result[0]["name"] == "Spring Festival"

    def test_returns_empty_list_when_competitions_is_empty(self):
        """Case 4 — 'competitions' key present but empty list: returns []."""
        data = json.dumps({"competitions": []})
        with patch("builtins.open", mock_open(read_data=data)):
            result = load_competitions()
        assert result == []

    def test_raises_file_not_found_when_file_missing(self):
        """Case 5 — file not found: returns None."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert load_competitions() is None

    def test_raises_json_decode_error_on_invalid_json(self):
        """Case 6 — invalid JSON content: returns None."""
        with patch("builtins.open", mock_open(read_data="not valid json {")):
            assert load_competitions() is None

    def test_raises_key_error_when_competitions_key_missing(self):
        """Case 7 — 'competitions' key missing from JSON: returns None."""
        data = json.dumps({"wrong_key": []})
        with patch("builtins.open", mock_open(read_data=data)):
            assert load_competitions() is None


class TestGetClubByEmail:

    def test_get_club_with_valid_email(self, mock_clubs):
        """Case 1 — valid email: returns the corresponding club."""
        valid_email = "john@simplylift.co"
        expected_club = {"name": "Simply Lift",
                         "email": "john@simplylift.co", "points": "13"}
        assert get_club_by_email(valid_email, mock_clubs) == expected_club

    def test_get_club_with_invalid_email(self, mock_clubs):
        """Case 2 — invalid email: returns None."""
        invalid_email = "invalid@simplylift.co"
        expected_result = None
        assert get_club_by_email(invalid_email, mock_clubs) == expected_result

    def test_get_club_with_empty_clubs_list(self):
        """Case 3 — empty clubs list: returns None."""
        empty_clubs = []
        email = "john@example.com"
        result = get_club_by_email(email, empty_clubs)
        assert result is None

    def test_get_club_with_multiple_clubs_same_email(self):
        """
        Case 4 — multiple clubs with the same email:
        Returns the first club found.
        """
        clubs_with_duplicate_email = [
            {
                "name": "Club A",
                "email": "duplicate@simplylift.co",
                "points": "10"
            },
            {
                "name": "Club B",
                "email": "duplicate@simplylift.co",
                "points": "20"
            }
        ]
        email = "duplicate@simplylift.co"
        result = get_club_by_email(email, clubs_with_duplicate_email)
        assert result == clubs_with_duplicate_email[0]

    def test_get_club_with_email_case_sensitivity(self, mock_clubs):
        """
        Case 5 — email with different case:
        Returns the corresponding club.
        """
        email_with_different_case = "John@SimplyLift.co"
        expected_club = {
            "name": "Simply Lift",
            "email": "john@simplylift.co",
            "points": "13"
        }
        result = get_club_by_email(email_with_different_case, mock_clubs)
        assert result == expected_club

    def test_get_club_with_email_with_white_space(self, mock_clubs):
        """
        Case 6 — email with spaces:
        Returns the corresponding club.
        """
        email_with_white_space = "  john@simplylift.co  "
        expected_club = {
            "name": "Simply Lift",
            "email": "john@simplylift.co",
            "points": "13"
        }
        result = get_club_by_email(email_with_white_space, mock_clubs)
        assert result == expected_club


class TestLowerCaseEmail:

    def test_lower_case_email(self):
        """
        Case 1 — email with uppercase:
        Returns the email in lower_case.
        """
        email = "John@SimplyLift.co"
        expected_email = "john@simplylift.co"
        result = lower_case_email(email)
        assert result == expected_email

    def test_lower_case_email_already_lower_case(self):
        """
        Case 2 — email already in lower_case:
        Returns the same email.
        """
        email = "john@simplylift.co"
        expected_email = "john@simplylift.co"
        result = lower_case_email(email)
        assert result == expected_email

    def test_lower_case_email_with_white_space(self):
        """
        Case 3 — email with spaces:
        Returns the email in lower_case with spaces.
        """
        email = "  John@SimplyLift.co  "
        expected_email = "  john@simplylift.co  "
        result = lower_case_email(email)
        assert result == expected_email

    def test_lower_case_email_empty_string(self):
        """Case 4 — empty email: returns an empty string."""
        email = ""
        expected_email = ""
        result = lower_case_email(email)
        assert result == expected_email


class TestStripWhiteSpace:

    def test_strip_white_space(self):
        """
        Case 1 — email with spaces before and after:
        Returns the email without spaces.
        """
        email = "  john@simplylift.co  "
        expected_email = "john@simplylift.co"
        result = strip_white_space(email)
        assert result == expected_email

    def test_strip_white_space_no_spaces(self):
        """Case 2 — email without spaces: returns the same email."""
        email = "john@simplylift.co"
        expected_email = "john@simplylift.co"
        result = strip_white_space(email)
        assert result == expected_email

    def test_strip_white_space_only_spaces(self):
        """Case 3 — email with only spaces: returns an empty string."""
        email = "     "
        expected_email = ""
        result = strip_white_space(email)
        assert result == expected_email

    def test_strip_white_space_empty_string(self):
        """Case 4 — empty email: returns an empty string."""
        email = ""
        expected_email = ""
        result = strip_white_space(email)
        assert result == expected_email

    def test_strip_white_space_with_tabs_and_newlines(self):
        """
        Case 5 — email with tabs and newlines:
        Returns the email without tabs and newlines.
        """
        email = "\n\t  john@simplylift.co  \n\t"
        expected_email = "john@simplylift.co"
        result = strip_white_space(email)
        assert result == expected_email

    def test_strip_white_space_with_internal_spaces(self):
        """
        Case 6 — email with internal spaces:
        Only removes spaces before and after.
        """
        email = "  john @ simplylift . co  "
        expected_email = "john @ simplylift . co"
        result = strip_white_space(email)
        assert result == expected_email


class TestGetClubByName:

    def test_get_club_with_valid_name(self, mock_clubs):
        """
        Case 1 — valid club name
        Returns the corresponding club.
        """
        name = "Simply Lift"
        expected_club = {
            "name": "Simply Lift",
            "email": "john@simplylift.co",
            "points": "13"
        }
        result = get_club_by_name(name, mock_clubs)
        assert result == expected_club

    def test_get_club_with_invalid_name(self, mock_clubs):
        """Case 2 — invalid club name: returns None."""
        name = "Nonexistent Club"
        expected_result = None
        result = get_club_by_name(name, mock_clubs)
        assert result == expected_result


class TestGetCompetitionByName:

    def test_get_competition_with_valid_name(self, mock_competitions):
        """
        Case 1 — valid competition name:
        Returns the corresponding competition.
        """
        name = "Spring Festival"
        expected_competition = {
            "name": "Spring Festival",
            "date": "2025-03-27 10:00:00",
            "number_of_places": "25"
        }
        result = get_competition_by_name(name, mock_competitions)
        assert result == expected_competition

    def test_get_competition_with_invalid_name(self, mock_competitions):
        """Case 2 — invalid competition name: returns None."""
        name = "Nonexistent Competition"
        expected_result = None
        result = get_competition_by_name(name, mock_competitions)
        assert result == expected_result


class TestGetClubPoints:

    def test_get_club_points_with_valid_club(self, mock_clubs):
        """Case 1 — valid club as parameter: returns the number of points."""
        valid_club = {"name": "Simply Lift",
                      "email": "john@simplylift.co", "points": "13"}
        expected_points = 13
        result = get_club_points(valid_club)
        assert result == expected_points

    def test_get_club_points_with_invalid_club(self, mock_clubs):
        """Case 2 — invalid club as parameter: returns None."""
        invalid_club = {"name": "Invalid Club", "email": "invalid@club.co"}
        expected_points = None
        result = get_club_points(invalid_club)
        assert result == expected_points


class TestGetCompetitionPlaces:

    def test_get_competition_places_with_valid_competition(
            self, mock_competitions):
        """
        Case 1 — valid competition as parameter:
        Returns the number of available places.
        """
        valid_competition = {
            "name": "Spring Festival",
            "date": "2025-03-27 10:00:00",
            "number_of_places": "25"
        }
        expected_places = 25
        result = get_competition_places(valid_competition)
        assert result == expected_places

    def test_get_competition_places_with_invalid_competition(
            self, mock_competitions):
        """Case 2 — invalid competition as parameter: returns None."""
        invalid_competition = {
            "name": "Invalid Competition", "date": "2025-01-01 00:00:00"}
        expected_places = None
        result = get_competition_places(invalid_competition)
        assert result == expected_places


class TestIsCompetitionBookable:

    def test_returns_true_for_future_competition_with_places(self):
        """Case 1 — future date and places > 0: returns True."""
        now = datetime(2026, 6, 22, 12, 0, 0)
        competition = {
            "name": "Future Open",
            "date": "2026-06-23 10:00:00",
            "number_of_places": "5",
        }

        assert is_competition_bookable(competition, now=now) is True

    def test_returns_false_for_past_competition(self):
        """Case 2 — past date: returns False."""
        now = datetime(2026, 6, 22, 12, 0, 0)
        competition = {
            "name": "Past Open",
            "date": "2026-06-21 10:00:00",
            "number_of_places": "5",
        }

        assert is_competition_bookable(competition, now=now) is False

    def test_returns_false_when_no_places_available(self):
        """Case 3 — no places available: returns False."""
        now = datetime(2026, 6, 22, 12, 0, 0)
        competition = {
            "name": "No Places",
            "date": "2026-06-23 10:00:00",
            "number_of_places": "0",
        }

        assert is_competition_bookable(competition, now=now) is False


class TestIsBookingValid:

    def test_validate_booking_with_valid_points_and_places(self):
        """
        Case 1 — club has enough points and places available:
        Returns an empty list.
        """
        club_points = 10
        competition_places = 5
        places_required = 3
        expected_errors = []
        result = is_booking_valid(
            club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_insufficient_club_points(self):
        """
        Case 2 — club has insufficient points:
        Returns a list with an error message.
        """
        club_points = 2
        competition_places = 5
        places_required = 3
        expected_errors = [
            "Not enough points available in your club to "
            "book the requested number of places."]
        result = is_booking_valid(
            club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_insufficient_competition_places(self):
        """
        Case 3 — insufficient available places:
        Returns a list with an error message.
        """
        club_points = 10
        competition_places = 2
        places_required = 3
        expected_errors = ["Not enough places available in this competition."]
        result = is_booking_valid(
            club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_invalid_club_and_competition_points(self):
        """
        Case 4 — club has insufficient points and competition has insufficient
        available places:
        Returns a list with both error messages.
        """
        club_points = 2
        competition_places = 2
        places_required = 3
        expected_errors = [
            "Not enough places available in this competition.",
            "Not enough points available in your club "
            "to book the requested number of places.",
        ]
        result = is_booking_valid(
            club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_zero_places_requested(self):
        """
        Case 5 — request to book zero places:
        Returns a list with an error message.
        """
        club_points = 10
        competition_places = 5
        places_required = 0
        expected_errors = ["You need to book at least one place."]
        result = is_booking_valid(
            club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_negative_places_requested(self):
        """
        Case 6 — request to book a negative number of places
        Returns a list with an error message.
        """
        club_points = 10
        competition_places = 5
        places_required = -1
        expected_errors = ["You cannot book a negative number of places."]
        result = is_booking_valid(
            club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_places_requested_exceeding_max_value(self):
        """
        Case 7 — request to book more than the maximum number of places
        Returns a list with an error message.
        """
        club_points = 15
        competition_places = 25
        places_required = 13
        expected_errors = [
            "You cannot book more than 12 places per competition."]
        result = is_booking_valid(
            club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_cumulative_places_exceeding_twelve(self):
        """
        Case 8 — club/competition cumulative > 12
        Returns an error even if the unit request is <= 12.
        """
        club_points = 20
        competition_places = 20
        places_required = 3
        places_already_booked = 10
        expected_errors = [
            "You cannot book more than 12 places per competition."]
        result = is_booking_valid(
            club_points,
            competition_places,
            places_required,
            places_already_booked=places_already_booked,
        )
        assert result == expected_errors


class TestUpdateClubPoints:

    def test_update_club_points_with_valid_deduction(self):
        """
        Case 1 — valid points deduction
        Updates the club's points.
        """
        club = {
            "name": "Simply Lift",
            "email": "john@simplylift.com",
            "points": "15"
        }
        points_to_deduct = 5
        expected_points_after_deduction = "10"
        result = update_club_points(club, points_to_deduct)
        assert result is True
        assert club["points"] == expected_points_after_deduction

    def test_update_club_points_with_deduction_exceeding_current_points(self):
        """
        Case 2 — deduction exceeds current points
        Does not update points and returns False.
        """
        club = {
            "name": "Simply Lift",
            "email": "john@simplylift.com",
            "points": "5"
        }
        points_to_deduct = 10
        expected_points_after_deduction = "5"
        result = update_club_points(club, points_to_deduct)
        assert result is False
        assert club["points"] == expected_points_after_deduction

    def test_update_club_points_with_invalid_club(self):
        """
        Case 3 — invalid club (not a dictionary)
        Does not update points and returns False.
        """
        invalid_club = "Not a club dictionary"
        points_to_deduct = 5
        result = update_club_points(invalid_club, points_to_deduct)
        assert result is False

    def test_update_club_points_with_non_integer_points(self):
        """
        Case 4 — club points not integers
        Does not update points and returns False.
        """
        club = {
            "name": "Simply Lift",
            "email": "john@simplylift.com",
            "points": "not a number"
        }
        points_to_deduct = 5
        result = update_club_points(club, points_to_deduct)
        assert result is False
        assert club["points"] == "not a number"

    def test_update_club_points_with_negative_deduction(self):
        """
        Case 5 — negative points deduction
        Does not update points and returns False.
        """
        club = {
            "name": "Simply Lift",
            "email": "john@simplylift.com",
            "points": "15"
        }
        points_to_deduct = -5
        expected_points_after_deduction = "15"
        result = update_club_points(club, points_to_deduct)
        assert result is False
        assert club["points"] == expected_points_after_deduction

    def test_update_club_points_with_zero_deduction(self):
        """
        Case 6 — zero points deduction
        Does not update points and returns True.
        """
        club = {
            "name": "Simply Lift",
            "email": "john@simplylift.com",
            "points": "15"
        }
        points_to_deduct = 0
        expected_points_after_deduction = "15"
        result = update_club_points(club, points_to_deduct)
        assert result is True
        assert club["points"] == expected_points_after_deduction


class TestUpdateCompetitionPlaces:

    def test_update_competition_places_with_valid_deduction(self):
        """
        Case 1 — valid places deduction
        Updates the competition's number of places.
        """
        competition = {
            "name": "Fall Classic",
            "date": "2026-10-22 13:30:00",
            "number_of_places": "13"
        }
        places_to_deduct = 5
        expected_places_after_deduction = "8"
        result = update_competition_places(competition, places_to_deduct)
        assert result is True
        number_of_places = competition["number_of_places"]
        assert number_of_places == expected_places_after_deduction

    def test_update_competition_places_with_deduction_exceeding_places(self):
        """
        Case 2 — deduction exceeds current places
        Does not update places and returns False.
        """
        competition = {
            "name": "Spring Festival",
            "date": "2025-03-27 10:00:00",
            "number_of_places": "5"
        }
        places_to_deduct = 10
        expected_places_after_deduction = "5"
        result = update_competition_places(competition, places_to_deduct)
        assert result is False
        number_of_places = competition["number_of_places"]
        assert number_of_places == expected_places_after_deduction

    def test_update_competition_places_with_invalid_competition(self):
        """
        Case 3 — invalid competition (not a dictionary)
        Does not update places and returns False.
        """
        invalid_competition = "Not a competition dictionary"
        places_to_deduct = 5
        result = update_competition_places(
            invalid_competition, places_to_deduct)
        assert result is False

    def test_update_competition_places_with_non_integer_places(self):
        """
        Case 4 — competition places not integers
        Does not update places and returns False.
        """
        competition = {
            "name": "Fall Classic",
            "date": "2026-10-22 13:30:00",
            "number_of_places": "not a number"
        }
        places_to_deduct = 5
        result = update_competition_places(competition, places_to_deduct)
        assert result is False
        assert competition["number_of_places"] == "not a number"

    def test_update_competition_places_with_negative_deduction(self):
        """
        Case 5 — negative places deduction
        Does not update places and returns False.
        """
        competition = {"name": "Fall Classic",
                       "date": "2026-10-22 13:30:00", "number_of_places": "13"}
        places_to_deduct = -5
        expected_places_after_deduction = "13"
        result = update_competition_places(competition, places_to_deduct)
        assert result is False
        number_of_places = competition["number_of_places"]
        assert number_of_places == expected_places_after_deduction

    def test_update_competition_places_with_zero_deduction(self):
        """
        Case 6 — zero places deduction
        Does not update places and returns True.
        """
        competition = {"name": "Fall Classic",
                       "date": "2026-10-22 13:30:00", "number_of_places": "13"}
        places_to_deduct = 0
        expected_places_after_deduction = "13"
        result = update_competition_places(competition, places_to_deduct)
        assert result is True
        number_of_places = competition["number_of_places"]
        assert number_of_places == expected_places_after_deduction


class TestGetBookingKey:

    def test_get_booking_key_with_valid_club_and_competition(
            self, mock_clubs, mock_competitions):
        """
        Case 1 — valid club and competition
        Returns the booking keys.
        """
        valid_club = mock_clubs[0]
        valid_competition = mock_competitions[0]
        expected_keys = f"{valid_club['name']}::{valid_competition['name']}"
        result = get_booking_key(valid_club['name'], valid_competition['name'])
        assert result == expected_keys


class TestGetLoggedClub:

    def test_get_logged_club_with_valid_session(
            self, request_session, mock_clubs):
        """
        Case 1 — valid session with a club
        Returns:  the corresponding club name.
        """
        with request_session(mock_clubs[0]['email']):
            result = get_logged_club()
            assert result == mock_clubs[0]

    def test_get_logged_club_with_no_session(self, request_session):
        """Case 2 — no session: returns None."""
        with request_session():
            result = get_logged_club()
            assert result is None

    def test_get_logged_club_with_invalid_session_data(self, request_session):
        """Case 3 — invalid session data: returns None."""
        with request_session("invalid_email@example.com"):
            result = get_logged_club()
            assert result is None
