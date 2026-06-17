import json

def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


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