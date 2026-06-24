import json
from datetime import datetime


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def loadClubs():
    try:
        with open('clubs.json') as c:
            listOfClubs = json.load(c)['clubs']
            return listOfClubs
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def loadCompetitions():
    try:
        with open('competitions.json') as comps:
            listOfCompetitions = json.load(comps)['competitions']
            return listOfCompetitions
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def getClubByEmail(email, clubs):
    email = lowercaseEmail(stripWhitespace(email))
    for club in clubs:
        if lowercaseEmail(stripWhitespace(club['email'])) == email:
            return club
    return None

def lowercaseEmail(email):
    """Convertit l'email en minuscules pour une comparaison insensible à la casse."""
    return email.lower()

def stripWhitespace(email):
    """Supprime les espaces avant et après l'email pour une comparaison précise."""
    return email.strip()

def getCompetitionByName(name, competitions):
    """Récupère une compétition par son nom dans la liste des compétitions."""
    for competition in competitions:
        if competition['name'] == name:
            return competition
    return None

def getClubByName(name, clubs):
    """Récupère un club par son nom dans la liste des clubs."""
    for club in clubs:
        if club['name'] == name:
            return club
    return None

def getClubPoints(club):
    """Récupère le nombre de points d'un club."""
    if not isinstance(club, dict):
        return None
    try:
        return int(club.get('points', None))
    except (TypeError, ValueError):
        return None

def getCompetitionPlaces(competition):
    """Récupère le nombre de places disponibles pour une compétition."""
    if not isinstance(competition, dict):
        return None
    try:
        return int(competition.get('numberOfPlaces', None))
    except (TypeError, ValueError):
        return None


def isCompetitionBookable(competition, now=None):
    """Retourne True si la compétition est dans le futur (ou présent) avec au moins 1 place."""
    if now is None:
        now = datetime.now()

    competition_places = getCompetitionPlaces(competition)
    if competition_places is None or competition_places <= 0:
        return False

    try:
        competition_date = datetime.strptime(competition['date'], DATE_FORMAT)
    except (KeyError, TypeError, ValueError):
        return False

    return competition_date >= now

def isBookingValid(club_points, competition_places, placesRequested, placesAlreadyBooked=0):
    """Valide si un club peut réserver des places pour une compétition."""
    errors = []

    if placesRequested <= 0:
        if placesRequested == 0:
            errors.append("You need to book at least one place.")
        else:
            errors.append("You cannot book a negative number of places.")

    if placesRequested > competition_places:
        errors.append("Not enough places available in this competition.")

    if placesRequested > club_points:
        errors.append("Not enough points available in your club to book the requested number of places.")

    if placesRequested > 12 or (placesAlreadyBooked + placesRequested) > 12:
        errors.append("You cannot book more than 12 places per competition.")

    return errors

def updateClubPoints(club, pointsToDeduct):
    """Met à jour les points d'un club après une réservation."""
    if not isinstance(club, dict):
        return False
    try:
        current_points = int(club.get('points', 0))
        new_points = current_points - pointsToDeduct
        if new_points < 0 or pointsToDeduct < 0:
            return False
        club['points'] = str(new_points)
        return True
    except (TypeError, ValueError):
        return False
    
def updateCompetitionPlaces(competition, placesToDeduct):
    """Met à jour le nombre de places disponibles pour une compétition après une réservation."""
    if not isinstance(competition, dict):
        return False
    try:
        current_places = int(competition.get('numberOfPlaces', 0))
        new_places = current_places - placesToDeduct
        if new_places < 0 or placesToDeduct < 0:
            return False
        competition['numberOfPlaces'] = str(new_places)
        return True
    except (TypeError, ValueError):
        return False