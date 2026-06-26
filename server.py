from flask import Flask, current_app, flash, redirect, render_template, request, session, url_for
from utils import (
    loadClubs,
    loadCompetitions,
    getClubByEmail,
    getCompetitionByName,
    getClubByName,
    getClubPoints,
    getCompetitionPlaces,
    isCompetitionBookable,
    isBookingValid,
    updateClubPoints,
    updateCompetitionPlaces,
    getBookingKey,
    requireLogin,
    logoutAndRedirect,
    buildCompetitionsView,
    clearSessionKeepingFlashes,
)


def create_app(config=None, clubs=None, competitions=None):
    app = Flask(__name__)
    app.secret_key = 'something_special'
    if config:
        app.config.update(config)

    app.config['COMPETITIONS'] = competitions if competitions is not None else loadCompetitions()
    app.config['CLUBS'] = clubs if clubs is not None else loadClubs()
    app.config.setdefault('BOOKINGS_BY_CLUB_COMPETITION', {})

    def render_welcome(club, competitions):
        return render_template(
            'welcome.html',
            club=club,
            competitions=buildCompetitionsView(competitions),
        )

    @app.route('/')
    def index():
        clearSessionKeepingFlashes()
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        club = requireLogin()
        if club is None:
            return logoutAndRedirect()
        available_competitions = current_app.config['COMPETITIONS']
        return render_welcome(club, available_competitions)

    @app.route('/pointsBoard')
    def pointsBoard():
        available_clubs = current_app.config['CLUBS']

        if available_clubs is None:
            flash("Error loading clubs data.")
            return redirect(url_for('index'))

        return render_template('points_board.html', clubs=available_clubs)

    @app.route('/showSummary', methods=['POST'])
    def showSummary():
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']

        if available_clubs is None or available_competitions is None:
            flash("Error loading clubs or competitions data.")
            return logoutAndRedirect()

        club = getClubByEmail(request.form['email'], available_clubs)
        if club:
            session['club_email'] = club['email']
            session['club_name'] = club['name']
            return render_welcome(club, available_competitions)

        flash("Unfortunately, the email you entered was not found.")
        return logoutAndRedirect()

    @app.route('/book/<competition>/<club>')
    def book(competition, club):
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']
        logged_club = requireLogin()

        if logged_club is None:
            return logoutAndRedirect()

        if available_clubs is None or available_competitions is None:
            flash("Error loading clubs or competitions data.")
            return logoutAndRedirect()

        found_competition = getCompetitionByName(
            competition, available_competitions)
        found_club = getClubByName(club, available_clubs)

        if found_club is None or found_club['name'] != logged_club['name']:
            flash("Invalid booking URL. Please check the club name.")
            return render_welcome(logged_club, available_competitions)

        if found_competition is None:
            flash("Invalid booking URL. Please check the competition name.")
            return render_welcome(found_club, available_competitions)

        if not isCompetitionBookable(found_competition):
            flash("This competition is no longer open for booking.")
            return render_welcome(found_club, available_competitions)

        return render_template('booking.html', club=found_club, competition=found_competition)

    @app.route('/purchasePlaces', methods=['POST'])
    def purchasePlaces():
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']
        logged_club = requireLogin()

        if logged_club is None:
            return logoutAndRedirect()

        if available_clubs is None or available_competitions is None:
            flash("Error loading clubs or competitions data.")
            return logoutAndRedirect()

        competition = getCompetitionByName(
            request.form['competition'], available_competitions)
        club = logged_club
        placesRequired = int(request.form['places'])
        booking_key = getBookingKey(club['name'], request.form['competition'])
        places_already_booked = current_app.config['BOOKINGS_BY_CLUB_COMPETITION'].get(
            booking_key, 0)

        if competition is None or club is None:
            flash("Invalid booking request. Please check the club and competition names.")
            return logoutAndRedirect()

        if not isCompetitionBookable(competition):
            flash("This competition is no longer open for booking.")
            return render_welcome(club, available_competitions)

        validation_errors = isBookingValid(
            getClubPoints(club),
            getCompetitionPlaces(competition),
            placesRequired,
            placesAlreadyBooked=places_already_booked,
        )

        if validation_errors:
            for error in validation_errors:
                flash(error)
            return render_welcome(club, available_competitions)

        updateClubPoints(club, placesRequired)
        updateCompetitionPlaces(competition, placesRequired)
        current_app.config['BOOKINGS_BY_CLUB_COMPETITION'][booking_key] = places_already_booked + placesRequired
        flash(f'Booking complete: {placesRequired} places purchased.')
        return render_welcome(club, available_competitions)

    @app.route('/logout')
    def logout():
        flash("You have been logged out.")
        return logoutAndRedirect()

    return app


app = create_app()
