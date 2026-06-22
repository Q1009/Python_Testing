from flask import Flask,render_template,request,redirect,flash,url_for,current_app
from datetime import datetime
from utils import (
    loadClubs,
    loadCompetitions,
    getClubByEmail,
    getCompetitionByName,
    getClubByName,
    getClubPoints,
    getCompetitionPlaces,
    isCompetitionBookable,
    validateBooking,
)

def create_app(config=None, clubs=None, competitions=None):
    app = Flask(__name__)
    app.secret_key = 'something_special'
    if config:
        app.config.update(config)

    app.config['COMPETITIONS'] = competitions if competitions is not None else loadCompetitions()
    app.config['CLUBS'] = clubs if clubs is not None else loadClubs()

    def buildCompetitionsView(competitions):
        now = datetime.now()
        competitions_view = []

        for competition in competitions:
            competition_view = dict(competition)
            competition_view['canBook'] = isCompetitionBookable(competition, now=now)
            competitions_view.append(competition_view)

        return competitions_view

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/showSummary',methods=['POST'])
    def showSummary():
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']

        if available_clubs is None or available_competitions is None:
            flash("Error loading clubs or competitions data.")
            return redirect(url_for('index'))

        club = getClubByEmail(request.form['email'], available_clubs)
        if club:
            return render_template(
                'welcome.html',
                club=club,
                competitions=buildCompetitionsView(available_competitions),
            )

        flash("Unfortunately, the email you entered was not found.")
        return redirect(url_for('index'))


    @app.route('/book/<competition>/<club>')
    def book(competition,club):
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']

        if available_clubs is None or available_competitions is None:
            flash("Error loading clubs or competitions data.")
            return redirect(url_for('index'))
        
        found_competition = getCompetitionByName(competition, available_competitions)
        found_club = getClubByName(club, available_clubs)
        #on peut forcer via l'URL une compétition dans le passé ou une compétition sans places disponibles, mais on ne peut pas forcer une compétition ou un club qui n'existent pas

        if found_club is None:
            flash("Invalid booking URL. Please check the club name.")
            return redirect(url_for('index'))

        if found_competition is None:
            flash("Invalid booking URL. Please check the competition name.")
            return render_template(
                'welcome.html',
                club=found_club,
                competitions=buildCompetitionsView(available_competitions),
            )

        if not isCompetitionBookable(found_competition):
            flash("This competition is no longer open for booking.")
            return render_template(
                'welcome.html',
                club=found_club,
                competitions=buildCompetitionsView(available_competitions),
            )
        


        return render_template('booking.html', club=found_club, competition=found_competition)

    @app.route('/purchasePlaces',methods=['POST'])
    def purchasePlaces():
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']

        if available_clubs is None or available_competitions is None:
            flash("Error loading clubs or competitions data.")
            return redirect(url_for('index'))

        competition = getCompetitionByName(request.form['competition'], available_competitions)
        club = getClubByName(request.form['club'], available_clubs)
        placesRequired = int(request.form['places'])

        if competition is None or club is None:
            flash("Invalid booking request. Please check the club and competition names.")
            return redirect(url_for('index'))

        validation_errors = validateBooking(
            getClubPoints(club),
            getCompetitionPlaces(competition),
            placesRequired,
        )

        if validation_errors:
            for error in validation_errors:
                flash(error)
            return render_template('booking.html', club=club, competition=competition)

        competition['numberOfPlaces'] = str(getCompetitionPlaces(competition) - placesRequired)
        flash(f'Booking complete: {placesRequired} places purchased.')
        return render_template(
            'welcome.html',
            club=club,
            competitions=buildCompetitionsView(available_competitions),
        )
    
    # TODO: Add route for points display


    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))

    return app


app = create_app()