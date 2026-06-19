import json

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