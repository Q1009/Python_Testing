import json
from datetime import datetime
from flask import current_app, flash, redirect, session, url_for


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_booking_key(club_name, competition_name):
    return f"{club_name}::{competition_name}"


def get_logged_club():
    email = session.get('club_email')
    if not email:
        return None
    return get_club_by_email(email, current_app.config['CLUBS'])


def require_login():
    club = get_logged_club()
    if club is None:
        flash("Please log in first.")
        return None
    return club


def clear_session_keeping_flashes():
    flashed_messages = session.get('_flashes', [])
    session.clear()
    if flashed_messages:
        session['_flashes'] = flashed_messages


def logout_and_redirect():
    clear_session_keeping_flashes()
    return redirect(url_for('index'))


def build_competitions_view(competitions):
    now = datetime.now()
    competitions_view = []

    for competition in competitions:
        competition_view = dict(competition)
        competition_view['can_book'] = is_competition_bookable(
            competition, now=now)
        competitions_view.append(competition_view)

    return competitions_view


def load_clubs():
    try:
        with open('clubs.json') as c:
            list_of_clubs = json.load(c)['clubs']
            return list_of_clubs
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def load_competitions():
    try:
        with open('competitions.json') as comps:
            list_of_competitions = json.load(comps)['competitions']
            return list_of_competitions
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def get_club_by_email(email, clubs):
    email = lower_case_email(strip_white_space(email))
    for club in clubs:
        if lower_case_email(strip_white_space(club['email'])) == email:
            return club
    return None


def lower_case_email(email):
    """Converts the email to lowercase for case-insensitive comparison."""
    return email.lower()


def strip_white_space(email):
    """Removes spaces before and after the email for precise comparison."""
    return email.strip()


def get_competition_by_name(name, competitions):
    """Retrieves a competition by its name from the list of competitions."""
    for competition in competitions:
        if competition['name'] == name:
            return competition
    return None


def get_club_by_name(name, clubs):
    """Retrieves a club by its name from the list of clubs."""
    for club in clubs:
        if club['name'] == name:
            return club
    return None


def get_club_points(club):
    """Retrieves the points of a club."""
    if not isinstance(club, dict):
        return None
    try:
        return int(club.get('points', None))
    except (TypeError, ValueError):
        return None


def get_competition_places(competition):
    """Retrieves the number of available places for a competition."""
    if not isinstance(competition, dict):
        return None
    try:
        return int(competition.get('number_of_places', None))
    except (TypeError, ValueError):
        return None


def is_competition_bookable(competition, now=None):
    """Returns True if the competition is in the future (or present) with at least 1 place available."""
    if now is None:
        now = datetime.now()

    competition_places = get_competition_places(competition)
    if competition_places is None or competition_places <= 0:
        return False

    try:
        competition_date = datetime.strptime(competition['date'], DATE_FORMAT)
    except (KeyError, TypeError, ValueError):
        return False

    return competition_date >= now


def is_booking_valid(club_points, competition_places, places_requested, places_already_booked=0):
    """Validates if a club can book places for a competition."""
    errors = []

    if places_requested <= 0:
        if places_requested == 0:
            errors.append("You need to book at least one place.")
        else:
            errors.append("You cannot book a negative number of places.")

    if places_requested > competition_places:
        errors.append("Not enough places available in this competition.")

    if places_requested > club_points:
        errors.append(
            "Not enough points available in your club to book the requested number of places.")

    if places_requested > 12 or (places_already_booked + places_requested) > 12:
        errors.append("You cannot book more than 12 places per competition.")

    return errors


def update_club_points(club, points_to_deduct):
    """Updates a club's points after a booking."""
    if not isinstance(club, dict):
        return False
    try:
        current_points = int(club.get('points', 0))
        new_points = current_points - points_to_deduct
        if new_points < 0 or points_to_deduct < 0:
            return False
        club['points'] = str(new_points)
        return True
    except (TypeError, ValueError):
        return False


def update_competition_places(competition, places_to_deduct):
    """Updates the number of available places for a competition after a booking."""
    if not isinstance(competition, dict):
        return False
    try:
        current_places = int(competition.get('number_of_places', 0))
        new_places = current_places - places_to_deduct
        if new_places < 0 or places_to_deduct < 0:
            return False
        competition['number_of_places'] = str(new_places)
        return True
    except (TypeError, ValueError):
        return False
