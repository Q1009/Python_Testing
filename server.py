import os
import secrets

from flask import (
    Flask,
    current_app,
    flash,
    redirect,
    render_template,
    request, session,
    url_for,
)
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
    """
    Create and configure a Flask application instance for the GÜDLFT server.

    This factory function initializes a Flask app, applies the provided or
    default configuration, and loads clubs and competitions data either
    from the provided arguments or from their respective JSON files.

    :param config: Optional dictionary of configuration values to update
                    the app's config. If ``None``,
                    only default values are applied.
    :type config: dict | None
    :param clubs: Optional list of club dictionaries to use for the
                application. If ``None``, clubs are loaded from
                ``clubs.json`` via :func:`utils.load_clubs`.
    :type clubs: list[dict] | None
    :param competitions: Optional list of competition dictionaries to use
                        for the application. If ``None``, competitions are
                        loaded from ``competitions.json`` via
                        :func:`utils.load_competitions`.
    :type competitions: list[dict] | None

    :return: A fully configured Flask application instance with routes,
            templates, and session management set up.
    :rtype: flask.Flask
    """
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    if config:
        app.config.update(config)

    app.config['COMPETITIONS'] = (
        competitions if competitions is not None
        else load_competitions()
    )
    app.config['CLUBS'] = (
        clubs if clubs is not None
        else load_clubs()
    )
    app.config.setdefault('BOOKINGS_BY_CLUB_COMPETITION', {})

    def render_welcome(club, competitions):
        """
        Render the welcome template for a logged-in club.

        This helper function prepares the template context with
        the club's details and a formatted view of available
        competitions, then renders the welcome page.

        :param club: Dictionary containing the club's information
                    (name, email, points, etc.).
                    Used to personalize the dashboard.
        :type club: dict
        :param competitions: List of competition dictionaries
                            to display on the dashboard.
                            Will be processed by
                            :func:`utils.build_competitions_view`
                            before rendering.
        :type competitions: list[dict]

        :return: Rendered HTML response for the welcome page.
        :rtype: flask.Response
        """
        return render_template(
            'welcome.html',
            club=club,
            competitions=build_competitions_view(competitions),
        )

    @app.route('/')
    def index():
        """
        Render the login/index page.

        Clears any existing session data (except flashed messages)
        before rendering.

        Returns:
            Response: Rendered template for the login page.
        """
        clear_session_keeping_flashes()
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        """
        Render the dashboard for an authenticated club.

        This route handler checks if the user is logged in.
        If not, it redirects to the login page.
        Otherwise, it displays the club's dashboard with
        available competitions.

        :return: Rendered welcome template with club and
                competitions data if logged in, or a redirect
                response to the login page if not authenticated.
        :rtype: flask.Response
        """
        club = require_login()
        if club is None:
            return logout_and_redirect()
        available_competitions = current_app.config['COMPETITIONS']
        return render_welcome(club, available_competitions)

    @app.route('/points_board')
    def points_board():
        """
        Render the public points board showing all clubs and their points.

        This route handler displays a leaderboard of all registered clubs
        with their current points. If the clubs data fails to load,
        it flashes an error message and redirects to the login page.

        :return: Rendered template for the points board if clubs data
                is available, or a redirect response to the login page
                with an error flash message if clubs data is missing.
        :rtype: flask.Response
        """
        available_clubs = current_app.config['CLUBS']

        if available_clubs is None:
            flash("Error loading clubs data.")
            return redirect(url_for('index'))

        return render_template('points_board.html', clubs=available_clubs)

    @app.route('/show_summary', methods=['POST'])
    def show_summary():
        """
        Handle login form submission and authenticate a club.

        This route processes POST requests from the login form.
        It validates the submitted email against registered clubs.
        On success, it creates a session and displays the club's
        dashboard.
        On failure, it flashes an error message.

        :return: Rendered welcome template with club and competitions
                data if login succeeds, or a redirect response to the
                login page with an error flash message if login fails
                or if clubs/competitions data is missing.
        :rtype: flask.Response
        """
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
        """
        Render the booking page for a specific competition and club.

        This route displays the booking form for a given competition and club.
        It performs multiple validations: authentication, data loading,
        URL parameters, and competition availability.
        If any validation fails, it redirects to the welcome page
        with an appropriate error message.

        :param competition: Name of the competition to book (from URL path).
        :type competition: str
        :param club: Name of the club making the booking (from URL path).
        :type club: str

        :return: Rendered booking template if all validations pass,
                or a redirect response to the welcome page with an error
                flash message if validation fails (missing data, invalid URL,
                competition closed, etc.).
        :rtype: flask.Response
        """
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

        return render_template(
            'booking.html', club=found_club, competition=found_competition)

    @app.route('/purchase_places', methods=['POST'])
    def purchase_places():
        """
        Process a booking request to purchase places in a competition.

        This route handles POST requests to finalize a booking.
        It validates the request (authentication, data integrity,
        and business rules), updates the club's points and the
        competition's available places on success, and manages
        the booking state.
        On failure, it flashes appropriate error messages.

        :return: Redirect response to the welcome page with
                a success flash message if the booking is valid,
                or with error messages if validation fails
                (missing data, invalid booking, competition closed,
                insufficient points, etc.).
        :rtype: flask.Response
        """
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
        booking_key = get_booking_key(
            club['name'], request.form['competition'])
        places_already_booked = (
            current_app.config['BOOKINGS_BY_CLUB_COMPETITION'].get(
                booking_key, 0
            )
        )

        if competition is None or club is None:
            flash(
                "Invalid booking request. Please check the club "
                "and competition names.")
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
        current_app.config['BOOKINGS_BY_CLUB_COMPETITION'][booking_key] = (
            places_already_booked + places_required
        )
        flash(f'Booking complete: {places_required} places purchased.')
        return render_welcome(club, available_competitions)

    @app.route('/logout')
    def logout():
        """
        Log out the current user.

        Clears the session and flashes a logout message.

        Returns:
            Response: Redirect to the login page with
            a logout confirmation message.
        """
        flash("You have been logged out.")
        return logout_and_redirect()

    return app


app = create_app()
