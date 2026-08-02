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
    Create and configure the Flask application.

    Args:
        config (dict, optional): Configuration dictionary
        to update the app config.
        clubs (list, optional): List of clubs to use.
        If None, loads from clubs.json.
        competitions (list, optional): List of competitions to use.
        If None, loads from competitions.json.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    app.secret_key = 'something_special'
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
        Render the welcome/dashboard template for a logged-in club.

        Args:
            club (dict): Club dictionary containing name, email, and points.
            competitions (list): List of competition dictionaries.

        Returns:
            Response: Rendered template response for the welcome page.
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
        Render the dashboard for a logged-in club.

        Requires an active login session. If not logged in,
        redirects to the login page.

        Returns:
            Response: Rendered welcome template if logged in,
                     or redirect response to login page if not.
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

        Returns:
            Response: Rendered template for the points board
            if clubs are loaded, or redirect to index with error
            flash message if clubs data fails to load.
        """
        available_clubs = current_app.config['CLUBS']

        if available_clubs is None:
            flash("Error loading clubs data.")
            return redirect(url_for('index'))

        return render_template('points_board.html', clubs=available_clubs)

    @app.route('/show_summary', methods=['POST'])
    def show_summary():
        """
        Handle login form submission.

        Validates the submitted email against registered clubs.
        On success, creates a session and redirects to the dashboard.
        On failure, flashes an error and redirects to login.

        Returns:
            Response: Redirect to dashboard if login succeeds,
            or redirect to login with error message if login fails.
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

        Args:
            competition (str): Name of the competition to book.
            club (str): Name of the club making the booking.

        Returns:
            Response: Rendered booking template if all validations pass,
            or redirect to welcome/dashboard with error message if
            validation fails.
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

        Validates the request, updates club points and competition
        places on success, and flashes appropriate messages for any errors.

        Returns:
            Response: Redirect to welcome/dashboard with success
            or error messages.
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
