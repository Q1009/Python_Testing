"""
Performance test suite for the GudLift application using Locust.

This script simulates a realistic load of secretary users interacting with the
GudLift competition booking system. It validates:
- Endpoint availability and HTTP response codes
- UI consistency (expected text in responses)
- Business rule enforcement (places, points, deadlines)
- Authentication and session management
"""
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

    Task weights reflect expected usage frequency:
    - authenticated_flow (6): Most common (booking places)
    - homepage (5): Frequent navigation
    - points_board (4): Regular checks
    - logout (2): Less frequent
    """

    wait_time = between(1, 3)

    # Valid users from clubs.json
    user_emails = [
        "john@simplylift.co",
        "kate@shelifts.co.uk",
        "admin@irontemple.com",
    ]

    # Club names paired with their best booking target
    booking_targets = [
        ("Simply Lift", "Fall Classic", 2),
        ("She Lifts", "Fall Classic", 1),
        ("Iron Temple", "Fall Classic", 1),
    ]

    def on_start(self):
        """
        Initialize the virtual user's session state.
        Resets login status and counters for email/booking rotation.
        """
        self.logged_in = False
        self.email_idx = 0
        self.booking_idx = 0

    def _next_email(self):
        """
        Return the next email in round-robin rotation.
        Cycles through valid club emails for authentication.
        """
        email = self.user_emails[self.email_idx % len(self.user_emails)]
        self.email_idx += 1
        return email

    def _next_booking_target(self):
        """
        Return the next (club, competition, places)
        tuple in round-robin rotation.
        Provides varied booking scenarios across clubs and competitions.
        """
        target = self.booking_targets[self.booking_idx %
                                      len(self.booking_targets)]
        self.booking_idx += 1
        return target

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
                response.failure("Points board indisponible")

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
        email = self._next_email()

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
                login_response.failure("Login invalide")
                return

        self.logged_in = True
        club_name, competition_name, places = self._next_booking_target()
        encoded_club = quote(club_name, safe="")
        encoded_comp = quote(competition_name, safe="")

        with self.client.get(
            f"/book/{encoded_comp}/{encoded_club}",
            name="GET /book/<competition>/<club>",
            catch_response=True,
        ) as booking_page_response:
            if booking_page_response.status_code != 200:
                booking_page_response.failure("Page booking non-200")
                return
            if "How many places?" not in booking_page_response.text:
                booking_page_response.failure("Formulaire booking absent")
                return

        with self.client.post(
            "/purchase_places",
            data={"competition": competition_name, "places": str(places)},
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
                purchase_response.failure(
                    "Blocking business rule on purchase")
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
                response.failure("Logout incomplet")
                return

        self.logged_in = False
