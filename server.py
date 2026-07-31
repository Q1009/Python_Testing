from flask import Flask, current_app, flash, redirect, render_template, request, session, url_for
from utils import (
    load_clubs,
    load_competitions,
    get_club_by_email,
    get_competition_by_name,
    get_club_by_name,
    get_club_points,
    get_competition_places,
    is_competition_bookable,
    is_booking_valid,
    update_club_points,
    update_competition_places,
    get_booking_key,
    require_login,
    logout_and_redirect,
    build_competitions_view,
    clear_session_keeping_flashes,
)


def create_app(config=None, clubs=None, competitions=None):
    app = Flask(__name__)
    app.secret_key = 'something_special'
    if config:
        app.config.update(config)

    app.config['COMPETITIONS'] = competitions if competitions is not None else load_competitions()
    app.config['CLUBS'] = clubs if clubs is not None else load_clubs()
    app.config.setdefault('BOOKINGS_BY_CLUB_COMPETITION', {})

    def render_welcome(club, competitions):
        return render_template(
            'welcome.html',
            club=club,
            competitions=build_competitions_view(competitions),
        )

    @app.route('/')
    def index():
        clear_session_keeping_flashes()
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        club = require_login()
        if club is None:
            return logout_and_redirect()
        available_competitions = current_app.config['COMPETITIONS']
        return render_welcome(club, available_competitions)

    @app.route('/points_board')
    def points_board():
        available_clubs = current_app.config['CLUBS']

        if available_clubs is None:
            flash("Error loading clubs data.")
            return redirect(url_for('index'))

        return render_template('points_board.html', clubs=available_clubs)

    @app.route('/show_summary', methods=['POST'])
    def show_summary():
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']

        if available_clubs is None or available_competitions is None:
            flash("Error loading clubs or competitions data.")
            return logout_and_redirect()

        club = get_club_by_email(request.form['email'], available_clubs)
        if club:
            session['club_email'] = club['email']
            session['club_name'] = club['name']
            return render_welcome(club, available_competitions)

        flash("Unfortunately, the email you entered was not found.")
        return logout_and_redirect()

    @app.route('/book/<competition>/<club>')
    def book(competition, club):
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']
        logged_club = require_login()

        if logged_club is None:
            return logout_and_redirect()

        if available_clubs is None or available_competitions is None:
            flash("Error loading clubs or competitions data.")
            return logout_and_redirect()

        found_competition = get_competition_by_name(
            competition, available_competitions)
        found_club = get_club_by_name(club, available_clubs)

        if found_club is None or found_club['name'] != logged_club['name']:
            flash("Invalid booking URL. Please check the club name.")
            return render_welcome(logged_club, available_competitions)

        if found_competition is None:
            flash("Invalid booking URL. Please check the competition name.")
            return render_welcome(found_club, available_competitions)

        if not is_competition_bookable(found_competition):
            flash("This competition is no longer open for booking.")
            return render_welcome(found_club, available_competitions)

        return render_template('booking.html', club=found_club, competition=found_competition)

    @app.route('/purchase_places', methods=['POST'])
    def purchase_places():
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']
        logged_club = require_login()

        if logged_club is None:
            return logout_and_redirect()

        if available_clubs is None or available_competitions is None:
            flash("Error loading clubs or competitions data.")
            return logout_and_redirect()

        competition = get_competition_by_name(
            request.form['competition'], available_competitions)
        club = logged_club
        places_required = int(request.form['places'])
        booking_key = get_booking_key(club['name'], request.form['competition'])
        places_already_booked = current_app.config['BOOKINGS_BY_CLUB_COMPETITION'].get(
            booking_key, 0)

        if competition is None or club is None:
            flash("Invalid booking request. Please check the club and competition names.")
            return logout_and_redirect()

        if not is_competition_bookable(competition):
            flash("This competition is no longer open for booking.")
            return render_welcome(club, available_competitions)

        validation_errors = is_booking_valid(
            get_club_points(club),
            get_competition_places(competition),
            places_required,
            places_already_booked=places_already_booked,
        )

        if validation_errors:
            for error in validation_errors:
                flash(error)
            return render_welcome(club, available_competitions)

        update_club_points(club, places_required)
        update_competition_places(competition, places_required)
        current_app.config['BOOKINGS_BY_CLUB_COMPETITION'][booking_key] = places_already_booked + places_required
        flash(f'Booking complete: {places_required} places purchased.')
        return render_welcome(club, available_competitions)

    @app.route('/logout')
    def logout():
        flash("You have been logged out.")
        return logout_and_redirect()

    return app


app = create_app()
