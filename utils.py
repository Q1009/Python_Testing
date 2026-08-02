import json
from datetime import datetime
from typing import Dict, List, Optional, Union
from flask import current_app, flash, redirect, session, url_for, Response

DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'

Club = Dict[str, Union[str, int]]
Competition = Dict[str, Union[str, int]]


def get_booking_key(club_name: str, competition_name: str) -> str:
    """
    Generate a unique booking key for a club and competition combination.

    Args:
        club_name: Name of the club.
        competition_name: Name of the competition.

    Returns:
        Unique key string in the format 'club_name::competition_name'.
    """
    return f"{club_name}::{competition_name}"


def get_logged_club() -> Optional[Club]:
    """
    Retrieve the currently logged-in club from the session.

    Uses the email stored in the session to find the corresponding club.

    Returns:
        Dictionary representing the logged-in club if found, otherwise None.
    """
    email = session.get('club_email')
    if not email:
        return None
    return get_club_by_email(email, current_app.config['CLUBS'])


def require_login() -> Optional[Club]:
    """
    Check if a user is logged in and return the club if so.

    If no user is logged in, flashes an error message and returns None.

    Returns:
        Dictionary representing the logged-in club if session
        is valid, otherwise None.
    """
    club = get_logged_club()
    if club is None:
        flash("Please log in first.")
        return None
    return club


def clear_session_keeping_flashes() -> None:
    """
    Clear the current session while preserving any flashed messages.

    This allows error or success messages to persist across redirects.
    """
    flashed_messages = session.get('_flashes', [])
    session.clear()
    if flashed_messages:
        session['_flashes'] = flashed_messages


def logout_and_redirect() -> Response:
    """
    Clear the session and redirect to the index page.

    Preserves any flashed messages during the redirect.

    Returns:
        Flask redirect response to the index route.
    """
    clear_session_keeping_flashes()
    return redirect(url_for('index'))


def build_competitions_view(
        competitions: List[Competition]) -> List[Competition]:
    """
    Build an enhanced view of competitions with booking availability.

    Adds a 'can_book' boolean to each competition indicating
    if it's currently bookable.

    Args:
        competitions: List of competition dictionaries.

    Returns:
        List of competition dictionaries with added 'can_book' field.
    """
    now = datetime.now()
    competitions_view = []

    for competition in competitions:
        competition_view = dict(competition)
        competition_view['can_book'] = is_competition_bookable(
            competition, now=now)
        competitions_view.append(competition_view)

    return competitions_view


def load_clubs() -> Optional[List[Club]]:
    """
    Load clubs data from the clubs.json file.

    Returns:
        List of club dictionaries if the file is
        found and valid, otherwise None.

    Raises:
        None. All exceptions are caught and result in returning None.
    """
    try:
        with open('clubs.json') as c:
            list_of_clubs: List[Club] = json.load(c)['clubs']
            return list_of_clubs
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def load_competitions() -> Optional[List[Competition]]:
    """
    Load competitions data from the competitions.json file.

    Returns:
        List of competition dictionaries if the file is
        found and valid, otherwise None.

    Raises:
        None. All exceptions are caught and result in returning None.
    """
    try:
        with open('competitions.json') as comps:
            list_of_competitions: List[Competition] = json.load(comps)[
                'competitions']
            return list_of_competitions
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def get_club_by_email(email: str, clubs: List[Club]) -> Optional[Club]:
    """
    Find a club by its email address from a list of clubs.

    The comparison is case-insensitive and ignores whitespace.

    Args:
        email: Email address to search for.
        clubs: List of club dictionaries to search in.

    Returns:
        Club dictionary if found, otherwise None.
    """
    email = lower_case_email(strip_white_space(email))
    for club in clubs:
        if lower_case_email(strip_white_space(club['email'])) == email:
            return club
    return None


def lower_case_email(email: str) -> str:
    """
    Convert an email address to lowercase.

    Args:
        email: Email address to convert.

    Returns:
        Lowercase version of the email.
    """
    return email.lower()


def strip_white_space(email: str) -> str:
    """
    Remove leading and trailing whitespace from an email address.

    Args:
        email: Email address to clean.

    Returns:
        Email address without leading or trailing whitespace.
    """
    return email.strip()


def get_competition_by_name(
        name: str, competitions: List[Competition]) -> Optional[Competition]:
    """
    Find a competition by its name from a list of competitions.

    Args:
        name: Name of the competition to find.
        competitions: List of competition dictionaries to search in.

    Returns:
        Competition dictionary if found, otherwise None.
    """
    for competition in competitions:
        if competition['name'] == name:
            return competition
    return None


def get_club_by_name(name: str, clubs: List[Club]) -> Optional[Club]:
    """
    Find a club by its name from a list of clubs.

    Args:
        name: Name of the club to find.
        clubs: List of club dictionaries to search in.

    Returns:
        Club dictionary if found, otherwise None.
    """
    for club in clubs:
        if club['name'] == name:
            return club
    return None


def get_club_points(club: Club) -> Optional[int]:
    """
    Extract and convert the points value from a club dictionary.

    Args:
        club: Club dictionary containing a 'points' key.

    Returns:
        Integer value of the club's points if valid, otherwise None.
    """
    if not isinstance(club, dict):
        return None
    try:
        return int(club.get('points', None))
    except (TypeError, ValueError):
        return None


def get_competition_places(competition: Competition) -> Optional[int]:
    """
    Extract and convert the number_of_places value
    from a competition dictionary.

    Args:
        competition: Competition dictionary containing a
        'number_of_places' key.

    Returns:
        Integer value of the available places if valid, otherwise None.
    """
    if not isinstance(competition, dict):
        return None
    try:
        return int(competition.get('number_of_places', None))
    except (TypeError, ValueError):
        return None


def is_competition_bookable(
        competition: Competition, now: Optional[datetime] = None) -> bool:
    """
    Check if a competition is available for booking.

    A competition is bookable if:
    - It has at least 1 available place
    - Its date is in the future (or present)

    Args:
        competition: Competition dictionary to check.
        now: Reference datetime for comparison.
        Uses current time if not provided.

    Returns:
        True if the competition is bookable, False otherwise.
    """
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


def is_booking_valid(
    club_points: int,
    competition_places: int,
    places_requested: int,
    places_already_booked: int = 0
) -> List[str]:
    """
    Validate a booking request against available points and places.

    Args:
        club_points: Available points of the club.
        competition_places: Available places in the competition.
        places_requested: Number of places the club wants to book.
        places_already_booked: Number of places already booked by
        this club for this competition.

    Returns:
        List of error message strings. Empty list if the booking is valid.
    """
    errors: List[str] = []

    if places_requested <= 0:
        if places_requested == 0:
            errors.append("You need to book at least one place.")
        else:
            errors.append("You cannot book a negative number of places.")

    if places_requested > competition_places:
        errors.append("Not enough places available in this competition.")

    if places_requested > club_points:
        errors.append(
            "Not enough points available in your club "
            "to book the requested number of places.")

    if (places_requested > 12
            or (places_already_booked + places_requested) > 12):
        errors.append("You cannot book more than 12 places per competition.")

    return errors


def update_club_points(club: Club, points_to_deduct: int) -> bool:
    """
    Deduct points from a club after a successful booking.

    Args:
        club: Club dictionary to update.
        points_to_deduct: Number of points to subtract.

    Returns:
        True if the update was successful, False otherwise.
    """
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


def update_competition_places(
        competition: Competition, places_to_deduct: int) -> bool:
    """
    Deduct places from a competition after a successful booking.

    Args:
        competition: Competition dictionary to update.
        places_to_deduct: Number of places to subtract.

    Returns:
        True if the update was successful, False otherwise.
    """
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
