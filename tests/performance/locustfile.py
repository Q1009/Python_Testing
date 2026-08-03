"""
Performance test suite for the GudLift application using Locust.

This script simulates a realistic load of secretary users interacting with the
GudLift competition booking system. It validates:
- Endpoint availability and HTTP response codes
- UI consistency (expected text in responses)
- Business rule enforcement (places, points, deadlines)
- Authentication and session management
"""
import json
import os
from urllib.parse import quote

from locust import HttpUser, between, task


class ProjectPerformanceTest(HttpUser):
    """
    Load test profile emulating a GudLift secretary user journey.

    Simulates a user who:
    1. Browses public pages (homepage, points board)
    2. Logs in with a valid club email
    3. Books places for competitions (with validation checks)
    4. Logs out

    Uses dynamic data from clubs.json and competitions.json to:
    1. Authenticate with all available club emails
    2. Book maximum possible places for competitions based on:
        - Club's remaining points
        - Competition's remaining places
        - 12 places maximum per club per competition rule

    Task weights reflect expected usage frequency:
    - authenticated_flow (6): Most common (booking places)
    - homepage (5): Frequent navigation
    - points_board (4): Regular checks
    - logout (2): Less frequent
    """

    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clubs = []
        self.competitions = []
        self._load_data()

    def _load_data(self):
        """Load clubs and competitions from JSON files."""
        script_dir = os.path.dirname(
            os.path.abspath(__file__)
        )
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(script_dir))
        )

        # Load clubs
        clubs_path = os.path.join(
            project_root, "Python_Testing", "clubs.json")
        with open(clubs_path, 'r') as f:
            clubs_data = json.load(f)
            self.clubs = clubs_data["clubs"]

        # Load competitions
        comp_path = os.path.join(
            project_root, "Python_Testing", "competitions.json")
        with open(comp_path, 'r') as f:
            comp_data = json.load(f)
            self.competitions = comp_data["competitions"]

        # Prepare email list from all clubs
        self.user_emails = [club["email"] for club in self.clubs]

    def on_start(self):
        """
        Initialize the virtual user's session state.
        Resets login status and counters for email/booking rotation.
        """
        self.logged_in = False
        self.email_idx = 0
        self.current_club = None
        self.current_competition = None

    def _next_email(self):
        """
        Return the next email in round-robin rotation.
        Cycles through valid club emails for authentication.
        """
        email = self.user_emails[self.email_idx % len(self.user_emails)]
        self.email_idx += 1
        return email

    def _get_club_by_email(self, email):
        """Find club data by email address."""
        for club in self.clubs:
            if club["email"] == email:
                return club
        return None

    def _next_booking_target(self):
        """
        Return the next (club, competition, places) tuple dynamically.
        Calculates maximum places as min(club_points, competition_places, 12).
        """
        # Get next club in rotation
        email = self._next_email()
        club = self._get_club_by_email(email)
        if not club:
            return None, None, 0

        # Get next competition in rotation
        comp_idx = self.email_idx % len(self.competitions)
        competition = self.competitions[comp_idx]

        # Calculate maximum places the club can book:
        # - Limited by club points (1 point = 1 place)
        # - Limited by competition available places
        # - Limited by 12 places max rule
        club_points = int(club["points"])
        comp_places = int(competition["number_of_places"])

        max_places = min(club_points, comp_places, 12)

        # Ensure at least 1 place if possible
        max_places = max(
            1, max_places) if club_points > 0 and comp_places > 0 else 0

        return club, competition, max_places

    @task(5)
    def homepage(self):
        """
        Load the application homepage.
        Validates that the root endpoint returns a 200 response.
        """
        self.client.get("/", name="GET /")

    @task(4)
    def points_board(self):
        """
        Load the points board page.
        Validates HTTP 200 and presence of 'Points Board' in the response.
        """
        with self.client.get(
            "/points_board",
            name="GET /points_board",
            catch_response=True
        ) as response:
            if (response.status_code != 200
                    or "Points Board" not in response.text):
                response.failure("Points board unavailable")

    @task(6)
    def authenticated_flow(self):
        """Simulate a full secretary workflow:
        login -> book places -> validate.
        Tests:
        - Successful login with valid credentials
        - Competition booking form accessibility
        - Place purchasing with business rule validation
        - Response handling for success/error cases
        """
        club, competition, places = self._next_booking_target()

        if not club or not competition or places <= 0:
            return

        email = club["email"]

        # Login
        with self.client.post(
            "/show_summary",
            data={"email": email},
            name="POST /show_summary (login)",
            catch_response=True,
        ) as login_response:
            if login_response.status_code != 200:
                login_response.failure("Login non-200")
                return
            if "Welcome," not in login_response.text:
                login_response.failure("Login invalid")
                return

        self.logged_in = True
        self.current_club = club
        self.current_competition = competition

        encoded_club = quote(club["name"], safe="")
        encoded_comp = quote(competition["name"], safe="")

        # Access booking page
        with self.client.get(
            f"/book/{encoded_comp}/{encoded_club}",
            name="GET /book/<competition>/<club>",
            catch_response=True,
        ) as booking_page_response:
            if booking_page_response.status_code != 200:
                booking_page_response.failure("Page booking non-200")
                return
            if "How many places?" not in booking_page_response.text:
                booking_page_response.failure("Booking form absent")
                return

        # Attempt to purchase calculated places
        with self.client.post(
            "/purchase_places",
            data={
                "competition": competition["name"],
                "club": club["name"],
                "places": str(places)
            },
            name="POST /purchase_places",
            catch_response=True,
        ) as purchase_response:
            if purchase_response.status_code != 200:
                purchase_response.failure("Purchase non-200")
                return

            success_text = "Booking complete"
            known_validation_errors = (
                "Not enough places",
                "Not enough points",
                "cannot book more than 12",
                "no longer open for booking",
            )

            if success_text in purchase_response.text:
                purchase_response.success()
            elif any(
                msg in purchase_response.text
                for msg in known_validation_errors
            ):
                # This is expected if another user booked places concurrently
                purchase_response.success()
            else:
                purchase_response.failure(
                    "Unexpected response on purchase_places")

    @task(2)
    def logout(self):
        """
        Terminate the user session.
        Validates HTTP 200 and redirects to the login page.
        """
        if not self.logged_in:
            return

        with self.client.get(
            "/logout",
            name="GET /logout",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure("Logout non-200")
                return
            if "Please enter your secretary email" not in response.text:
                response.failure("Logout incomplete")
                return

        self.logged_in = False
