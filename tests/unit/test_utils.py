import json
from datetime import datetime
from unittest.mock import mock_open, patch
from utils import (
    loadClubs,
    loadCompetitions,
    getClubByEmail,
    lowercaseEmail,
    stripWhitespace,
    getCompetitionByName,
    getClubByName,
    getClubPoints,
    getCompetitionPlaces,
    isCompetitionBookable,
    isBookingValid,
    updateClubPoints,
    updateCompetitionPlaces,
    getBookingKey,
    getLoggedClub,
)


class TestLoadClubs:

    def test_returns_all_clubs(self, mock_clubs):
        """Cas 1 — fichier valide avec plusieurs clubs : retourne tous les éléments."""
        data = json.dumps({"clubs": mock_clubs})
        with patch("builtins.open", mock_open(read_data=data)):
            result = loadClubs()
        assert len(result) == 3

    def test_each_club_has_required_keys(self, mock_clubs):
        """Cas 2 — chaque club contient les clés name, email et points."""
        data = json.dumps({"clubs": mock_clubs})
        with patch("builtins.open", mock_open(read_data=data)):
            result = loadClubs()
        for club in result:
            assert "name" in club
            assert "email" in club
            assert "points" in club

    def test_returns_single_club(self):
        """Cas 3 — fichier valide avec un seul club : retourne une liste à un élément."""
        club = [{"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}]
        data = json.dumps({"clubs": club})
        with patch("builtins.open", mock_open(read_data=data)):
            result = loadClubs()
        assert len(result) == 1
        assert result[0]["name"] == "Simply Lift"

    def test_returns_empty_list_when_clubs_is_empty(self):
        """Cas 4 — clé 'clubs' présente mais liste vide : retourne []."""
        data = json.dumps({"clubs": []})
        with patch("builtins.open", mock_open(read_data=data)):
            result = loadClubs()
        assert result == []

    def test_raises_file_not_found_when_file_missing(self):
        """Cas 5 — fichier introuvable : retourne None."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert loadClubs() is None

    def test_raises_json_decode_error_on_invalid_json(self):
        """Cas 6 — contenu JSON invalide : retourne None."""
        with patch("builtins.open", mock_open(read_data="not valid json {")):
            assert loadClubs() is None

    def test_raises_key_error_when_clubs_key_missing(self):
        """Cas 7 — clé 'clubs' absente du JSON : retourne None."""
        data = json.dumps({"wrong_key": []})
        with patch("builtins.open", mock_open(read_data=data)):
            assert loadClubs() is None

class TestLoadCompetitions:

    def test_returns_all_competitions(self, mock_competitions):
        """Cas 1 — fichier valide avec plusieurs compétitions : retourne tous les éléments."""
        data = json.dumps({"competitions": mock_competitions})
        with patch("builtins.open", mock_open(read_data=data)):
            result = loadCompetitions()
        assert len(result) == 2

    def test_each_competition_has_required_keys(self, mock_competitions):
        """Cas 2 — chaque compétition contient les clés name, date et numberOfPlaces."""
        data = json.dumps({"competitions": mock_competitions})
        with patch("builtins.open", mock_open(read_data=data)):
            result = loadCompetitions()
        for competition in result:
            assert "name" in competition
            assert "date" in competition
            assert "numberOfPlaces" in competition

    def test_returns_single_competition(self):
        """Cas 3 — fichier valide avec une seule compétition : retourne une liste à un élément."""
        competition = [{"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "25"}]
        data = json.dumps({"competitions": competition})
        with patch("builtins.open", mock_open(read_data=data)):
            result = loadCompetitions()
        assert len(result) == 1
        assert result[0]["name"] == "Spring Festival"

    def test_returns_empty_list_when_competitions_is_empty(self):
        """Cas 4 — clé 'competitions' présente mais liste vide : retourne []."""
        data = json.dumps({"competitions": []})
        with patch("builtins.open", mock_open(read_data=data)):
            result = loadCompetitions()
        assert result == []

    def test_raises_file_not_found_when_file_missing(self):
        """Cas 5 — fichier introuvable : retourne None."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert loadCompetitions() is None

    def test_raises_json_decode_error_on_invalid_json(self):
        """Cas 6 — contenu JSON invalide : retourne None."""
        with patch("builtins.open", mock_open(read_data="not valid json {")):
            assert loadCompetitions() is None

    def test_raises_key_error_when_competitions_key_missing(self):
        """Cas 7 — clé 'competitions' absente du JSON : retourne None."""
        data = json.dumps({"wrong_key": []})
        with patch("builtins.open", mock_open(read_data=data)):
            assert loadCompetitions() is None

class TestGetClubByEmail:

    def test_get_club_with_valid_email(self, mock_clubs):
        """Cas 1 — email valide : retourne le club correspondant."""
        valid_email = "john@simplylift.co"
        expected_club = {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
        assert getClubByEmail(valid_email, mock_clubs) == expected_club

    def test_get_club_with_invalid_email(self, mock_clubs):
        """Cas 2 — email invalide : retourne None."""
        invalid_email = "invalid@simplylift.co"
        expected_result = None
        assert getClubByEmail(invalid_email, mock_clubs) == expected_result

    def test_get_club_with_empty_clubs_list(self):
        """Cas 3 — liste de clubs vide : retourne None."""
        empty_clubs = []
        email = "john@example.com"
        result = getClubByEmail(email, empty_clubs)
        assert result is None

    def test_get_club_with_multiple_clubs_same_email(self):
        """Cas 4 — plusieurs clubs avec le même email : retourne le premier club trouvé."""
        clubs_with_duplicate_email = [
            {"name": "Club A", "email": "duplicate@simplylift.co", "points": "10"},
            {"name": "Club B", "email": "duplicate@simplylift.co", "points": "20"}
        ]
        email = "duplicate@simplylift.co"
        result = getClubByEmail(email, clubs_with_duplicate_email)
        assert result == clubs_with_duplicate_email[0]
    
    def test_get_club_with_email_case_sensitivity(self, mock_clubs):
        """Cas 5 — email avec casse différente : retourne le club correspondant."""
        email_with_different_case = "John@SimplyLift.co"
        expected_club = {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
        result = getClubByEmail(email_with_different_case, mock_clubs)
        assert result == expected_club

    def test_get_club_with_email_with_whitespace(self, mock_clubs):
        """Cas 6 — email avec espaces : retourne le club correspondant."""
        email_with_whitespace = "  john@simplylift.co  "
        expected_club = {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
        result = getClubByEmail(email_with_whitespace, mock_clubs)
        assert result == expected_club

class TestLowercaseEmail:

    def test_lowercase_email(self):
        """Cas 1 — email avec majuscules : retourne l'email en minuscules."""
        email = "John@SimplyLift.co"
        expected_email = "john@simplylift.co"
        result = lowercaseEmail(email)
        assert result == expected_email
    
    def test_lowercase_email_already_lowercase(self):
        """Cas 2 — email déjà en minuscules : retourne le même email."""
        email = "john@simplylift.co"
        expected_email = "john@simplylift.co"
        result = lowercaseEmail(email)
        assert result == expected_email

    def test_lowercase_email_with_whitespace(self):
        """Cas 3 — email avec espaces : retourne l'email en minuscules avec espaces."""
        email = "  John@SimplyLift.co  "
        expected_email = "  john@simplylift.co  "
        result = lowercaseEmail(email)
        assert result == expected_email

    def test_lowercase_email_empty_string(self):
        """Cas 4 — email vide : retourne une chaîne vide."""
        email = ""
        expected_email = ""
        result = lowercaseEmail(email)
        assert result == expected_email

class TestStripWhitespace:

    def test_strip_whitespace(self):
        """Cas 1 — email avec espaces avant et après : retourne l'email sans espaces."""
        email = "  john@simplylift.co  "
        expected_email = "john@simplylift.co"
        result = stripWhitespace(email)
        assert result == expected_email

    def test_strip_whitespace_no_spaces(self):
        """Cas 2 — email sans espaces : retourne le même email."""
        email = "john@simplylift.co"
        expected_email = "john@simplylift.co"
        result = stripWhitespace(email)
        assert result == expected_email

    def test_strip_whitespace_only_spaces(self):
        """Cas 3 — email avec uniquement des espaces : retourne une chaîne vide."""
        email = "     "
        expected_email = ""
        result = stripWhitespace(email)
        assert result == expected_email

    def test_strip_whitespace_empty_string(self):
        """Cas 4 — email vide : retourne une chaîne vide."""
        email = ""
        expected_email = ""
        result = stripWhitespace(email)
        assert result == expected_email

    def test_strip_whitespace_with_tabs_and_newlines(self):
        """Cas 5 — email avec tabulations et nouvelles lignes : retourne l'email sans tabulations et nouvelles lignes."""
        email = "\n\t  john@simplylift.co  \n\t"
        expected_email = "john@simplylift.co"
        result = stripWhitespace(email)
        assert result == expected_email

    def test_strip_whitespace_with_internal_spaces(self):
        """Cas 6 — email avec espaces internes : ne supprime que les espaces avant et après."""
        email = "  john @ simplylift . co  "
        expected_email = "john @ simplylift . co"
        result = stripWhitespace(email)
        assert result == expected_email

class TestGetClubByName:

    def test_get_club_with_valid_name(self, mock_clubs):
        """Cas 1 — nom de club valide : retourne le club correspondant."""
        name = "Simply Lift"
        expected_club = {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
        result = getClubByName(name, mock_clubs)
        assert result == expected_club

    def test_get_club_with_invalid_name(self, mock_clubs):
        """Cas 2 — nom de club invalide : retourne None."""
        name = "Nonexistent Club"
        expected_result = None
        result = getClubByName(name, mock_clubs)
        assert result == expected_result

class TestGetCompetitionByName:

    def test_get_competition_with_valid_name(self, mock_competitions):
        """Cas 1 — nom de compétition valide : retourne la compétition correspondante."""
        name = "Spring Festival"
        expected_competition = {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "25"}
        result = getCompetitionByName(name, mock_competitions)
        assert result == expected_competition

    def test_get_competition_with_invalid_name(self, mock_competitions):
        """Cas 2 — nom de compétition invalide : retourne None."""
        name = "Nonexistent Competition"
        expected_result = None
        result = getCompetitionByName(name, mock_competitions)
        assert result == expected_result

class TestGetClubPoints:

    def test_get_club_points_with_valid_club(self, mock_clubs):
        """Cas 1 — club valide en paramètre : retourne le nombre de points."""
        valid_club = {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
        expected_points = 13
        result = getClubPoints(valid_club)
        assert result == expected_points

    def test_get_club_points_with_invalid_club(self, mock_clubs):
        """Cas 2 — club invalide en paramètre : retourne None."""
        invalid_club = {"name": "Invalid Club", "email": "invalid@club.co"}
        expected_points = None
        result = getClubPoints(invalid_club)
        assert result == expected_points

class TestGetCompetitionPlaces:

    def test_get_competition_places_with_valid_competition(self, mock_competitions):
        """Cas 1 — compétition valide en paramètre : retourne le nombre de places disponibles."""
        valid_competition = {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "25"}
        expected_places = 25
        result = getCompetitionPlaces(valid_competition)
        assert result == expected_places

    def test_get_competition_places_with_invalid_competition(self, mock_competitions):
        """Cas 2 — compétition invalide en paramètre : retourne None."""
        invalid_competition = {"name": "Invalid Competition", "date": "2025-01-01 00:00:00"}
        expected_places = None
        result = getCompetitionPlaces(invalid_competition)
        assert result == expected_places


class TestIsCompetitionBookable:

    def test_returns_true_for_future_competition_with_places(self):
        """Cas 1 — date future et places > 0 : retourne True."""
        now = datetime(2026, 6, 22, 12, 0, 0)
        competition = {
            "name": "Future Open",
            "date": "2026-06-23 10:00:00",
            "numberOfPlaces": "5",
        }

        assert isCompetitionBookable(competition, now=now) is True

    def test_returns_false_for_past_competition(self):
        """Cas 2 — date passée : retourne False."""
        now = datetime(2026, 6, 22, 12, 0, 0)
        competition = {
            "name": "Past Open",
            "date": "2026-06-21 10:00:00",
            "numberOfPlaces": "5",
        }

        assert isCompetitionBookable(competition, now=now) is False

    def test_returns_false_when_no_places_available(self):
        """Cas 3 — aucune place disponible : retourne False."""
        now = datetime(2026, 6, 22, 12, 0, 0)
        competition = {
            "name": "No Places",
            "date": "2026-06-23 10:00:00",
            "numberOfPlaces": "0",
        }

        assert isCompetitionBookable(competition, now=now) is False

class TestIsBookingValid:

    def test_validate_booking_with_valid_points_and_places(self):
        """Cas 1 — points du club suffisants et places disponibles : retourne une liste vide."""
        club_points = 10
        competition_places = 5
        places_required = 3
        expected_errors = []
        result = isBookingValid(club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_insufficient_club_points(self):
        """Cas 2 — points du club insuffisants : retourne une liste avec un message d'erreur."""
        club_points = 2
        competition_places = 5
        places_required = 3
        expected_errors = ["Not enough points available in your club to book the requested number of places."]
        result = isBookingValid(club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_insufficient_competition_places(self):
        """Cas 3 — places disponibles insuffisantes : retourne une liste avec un message d'erreur."""
        club_points = 10
        competition_places = 2
        places_required = 3
        expected_errors = ["Not enough places available in this competition."]
        result = isBookingValid(club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_insufficient_club_points_and_competition_places(self):
        """Cas 4 — points du club insuffisants et places disponibles insuffisantes : retourne une liste avec les deux messages d'erreur."""
        club_points = 2
        competition_places = 2
        places_required = 3
        expected_errors = [
            "Not enough places available in this competition.",
            "Not enough points available in your club to book the requested number of places.",
        ]
        result = isBookingValid(club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_zero_places_requested(self):
        """Cas 5 — demande de réservation de zéro place : retourne une liste avec un message d'erreur."""
        club_points = 10
        competition_places = 5
        places_required = 0
        expected_errors = ["You need to book at least one place."]
        result = isBookingValid(club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_negative_places_requested(self):
        """Cas 6 — demande de réservation d'un nombre négatif de places : retourne une liste avec un message d'erreur."""
        club_points = 10
        competition_places = 5
        places_required = -1
        expected_errors = ["You cannot book a negative number of places."]
        result = isBookingValid(club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_places_requested_exceeding_max_value(self):
        """Cas 7 — demande de réservation d'un nombre de places supérieur à une valeur maximale : retourne une liste avec un message d'erreur."""
        club_points = 15
        competition_places = 25
        places_required = 13
        expected_errors = ["You cannot book more than 12 places per competition."]
        result = isBookingValid(club_points, competition_places, places_required)
        assert result == expected_errors

    def test_validate_booking_with_cumulative_places_exceeding_twelve(self):
        """Cas 8 — cumul club/compétition > 12 : retourne une erreur même si la demande unitaire est <= 12."""
        club_points = 20
        competition_places = 20
        places_required = 3
        places_already_booked = 10
        expected_errors = ["You cannot book more than 12 places per competition."]
        result = isBookingValid(
            club_points,
            competition_places,
            places_required,
            placesAlreadyBooked=places_already_booked,
        )
        assert result == expected_errors

class TestUpdateClubPoints:

    def test_update_club_points_with_valid_deduction(self):
        """Cas 1 — déduction valide de points : met à jour les points du club."""
        club = {"name": "Simply Lift", "email": "john@simplylift.com", "points": "15"}
        points_to_deduct = 5
        expected_points_after_deduction = "10"
        result = updateClubPoints(club, points_to_deduct)
        assert result is True
        assert club["points"] == expected_points_after_deduction

    def test_update_club_points_with_deduction_exceeding_current_points(self):
        """Cas 2 — déduction supérieure aux points actuels : ne met pas à jour les points et retourne False."""
        club = {"name": "Simply Lift", "email": "john@simplylift.com", "points": "5"}
        points_to_deduct = 10
        expected_points_after_deduction = "5"
        result = updateClubPoints(club, points_to_deduct)
        assert result is False
        assert club["points"] == expected_points_after_deduction

    def test_update_club_points_with_invalid_club(self):
        """Cas 3 — club invalide (non-dictionnaire) : ne met pas à jour les points et retourne False."""
        invalid_club = "Not a club dictionary"
        points_to_deduct = 5
        result = updateClubPoints(invalid_club, points_to_deduct)
        assert result is False

    def test_update_club_points_with_non_integer_points(self):
        """Cas 4 — points du club non entiers : ne met pas à jour les points et retourne False."""
        club = {"name": "Simply Lift", "email": "john@simplylift.com", "points": "not a number"}
        points_to_deduct = 5
        result = updateClubPoints(club, points_to_deduct)
        assert result is False
        assert club["points"] == "not a number"

    def test_update_club_points_with_negative_deduction(self):
        """Cas 5 — déduction négative de points : ne met pas à jour les points et retourne False."""
        club = {"name": "Simply Lift", "email": "john@simplylift.com", "points": "15"}
        points_to_deduct = -5
        expected_points_after_deduction = "15"
        result = updateClubPoints(club, points_to_deduct)
        assert result is False
        assert club["points"] == expected_points_after_deduction

    def test_update_club_points_with_zero_deduction(self):
        """Cas 6 — déduction de zéro point : ne met pas à jour les points et retourne True."""
        club = {"name": "Simply Lift", "email": "john@simplylift.com", "points": "15"}
        points_to_deduct = 0
        expected_points_after_deduction = "15"
        result = updateClubPoints(club, points_to_deduct)
        assert result is True
        assert club["points"] == expected_points_after_deduction

class TestUpdateCompetitionPlaces:

    def test_update_competition_places_with_valid_deduction(self):
        """Cas 1 — déduction valide de places : met à jour le nombre de places de la compétition."""
        competition = {"name": "Fall Classic", "date": "2026-10-22 13:30:00", "numberOfPlaces": "13"}
        places_to_deduct = 5
        expected_places_after_deduction = "8"
        result = updateCompetitionPlaces(competition, places_to_deduct)
        assert result is True
        assert competition["numberOfPlaces"] == expected_places_after_deduction

    def test_update_competition_places_with_deduction_exceeding_current_places(self):
        """Cas 2 — déduction supérieure aux places actuelles : ne met pas à jour les places et retourne False."""
        competition = {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "5"}
        places_to_deduct = 10
        expected_places_after_deduction = "5"
        result = updateCompetitionPlaces(competition, places_to_deduct)
        assert result is False
        assert competition["numberOfPlaces"] == expected_places_after_deduction

    def test_update_competition_places_with_invalid_competition(self):
        """Cas 3 — compétition invalide (non-dictionnaire) : ne met pas à jour les places et retourne False."""
        invalid_competition = "Not a competition dictionary"
        places_to_deduct = 5
        result = updateCompetitionPlaces(invalid_competition, places_to_deduct)
        assert result is False

    def test_update_competition_places_with_non_integer_places(self):
        """Cas 4 — nombre de places de la compétition non entier : ne met pas à jour les places et retourne False."""
        competition = {"name": "Fall Classic", "date": "2026-10-22 13:30:00", "numberOfPlaces": "not a number"}
        places_to_deduct = 5
        result = updateCompetitionPlaces(competition, places_to_deduct)
        assert result is False
        assert competition["numberOfPlaces"] == "not a number"

    def test_update_competition_places_with_negative_deduction(self):
        """Cas 5 — déduction négative de places : ne met pas à jour les places et retourne False."""
        competition = {"name": "Fall Classic", "date": "2026-10-22 13:30:00", "numberOfPlaces": "13"}
        places_to_deduct = -5
        expected_places_after_deduction = "13"
        result = updateCompetitionPlaces(competition, places_to_deduct)
        assert result is False
        assert competition["numberOfPlaces"] == expected_places_after_deduction

    def test_update_competition_places_with_zero_deduction(self):
        """Cas 6 — déduction de zéro place : ne met pas à jour les places et retourne True."""
        competition = {"name": "Fall Classic", "date": "2026-10-22 13:30:00", "numberOfPlaces": "13"}
        places_to_deduct = 0
        expected_places_after_deduction = "13"
        result = updateCompetitionPlaces(competition, places_to_deduct)
        assert result is True
        assert competition["numberOfPlaces"] == expected_places_after_deduction

class TestGetBookingKey:

    def test_get_booking_key_with_valid_club_and_competition(self, mock_clubs, mock_competitions):
        """Cas 1 — club et compétition valides : retourne les clés de réservation."""
        valid_club = mock_clubs[0]
        valid_competition = mock_competitions[0]
        expected_keys = f"{valid_club['name']}::{valid_competition['name']}"
        result = getBookingKey(valid_club['name'], valid_competition['name'])
        assert result == expected_keys

class TestGetLoggedClub:

    def test_get_logged_club_with_valid_session(self, request_session, mock_clubs):
        """Cas 1 — session valide avec un club : retourne le nom du club correspondant."""
        with request_session(mock_clubs[0]['email']):
            result = getLoggedClub()
            assert result == mock_clubs[0]

    def test_get_logged_club_with_no_session(self, request_session):
        """Cas 2 — pas de session : retourne None."""
        with request_session():
            result = getLoggedClub()
            assert result is None

    def test_get_logged_club_with_invalid_session_data(self, request_session):
        """Cas 3 — données de session invalides : retourne None."""
        with request_session("invalid_email@example.com"):
            result = getLoggedClub()
            assert result is None