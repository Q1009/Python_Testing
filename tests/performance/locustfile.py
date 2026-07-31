from urllib.parse import quote

from locust import HttpUser, between, task


class ProjectPerformanceTest(HttpUser):
    """Load profile that emulates a secretary user journey in GudLift."""

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
        # Each virtual user starts with a fresh anonymous session.
        self.logged_in = False
        self.email_idx = 0
        self.booking_idx = 0

    def _next_email(self):
        email = self.user_emails[self.email_idx % len(self.user_emails)]
        self.email_idx += 1
        return email

    def _next_booking_target(self):
        target = self.booking_targets[self.booking_idx % len(self.booking_targets)]
        self.booking_idx += 1
        return target

    @task(5)
    def homepage(self):
        self.client.get("/", name="GET /")

    @task(4)
    def points_board(self):
        with self.client.get("/points_board", name="GET /points_board", catch_response=True) as response:
            if response.status_code != 200 or "Points Board" not in response.text:
                response.failure("Points board indisponible")

    @task(6)
    def authenticated_flow(self):
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
            elif any(msg in purchase_response.text for msg in known_validation_errors):
                purchase_response.failure("Règle métier bloquante sur purchase")
            else:
                purchase_response.failure("Réponse purchase inattendue")

    @task(2)
    def logout(self):
        if not self.logged_in:
            return

        with self.client.get("/logout", name="GET /logout", catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Logout non-200")
                return
            if "Please enter your secretary email" not in response.text:
                response.failure("Logout incomplet")
                return

        self.logged_in = False