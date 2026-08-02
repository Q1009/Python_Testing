from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from server import create_app


class TestBookPlacesValid(LiveServerTestCase):
    def create_app(self):
        return create_app()

    def setUp(self):
        # Ensure GeckoDriver is installed and in PATH.
        self.driver = webdriver.Firefox()
        self.driver.get(self.get_server_url())

    def tearDown(self):
        self.driver.quit()

    def test_user_can_book_five_places_and_view_updated_points_board(self):
        # 1) The user logs in from the homepage.
        email_input = self.driver.find_element(By.ID, "email")
        email_input.send_keys("john@simplylift.co")
        self.driver.find_element(By.ID, "login").click()

        self.assertIn("Welcome, Simply Lift", self.driver.page_source)

        # 2) The user opens a reservable upcoming competition (Fall Classic).
        competition_item = self.driver.find_element(
            By.XPATH,
            "//li[p[normalize-space()='Fall Classic']]",
        )
        self.assertIn("Number of Places: 13", competition_item.text)
        competition_item.find_element(By.LINK_TEXT, "Book Places").click()

        self.assertIn("Places available: 13", self.driver.page_source)
        places_input = self.driver.find_element(By.ID, "places")
        self.assertEqual(places_input.get_attribute("max"), "12")

        # 3) The user buys 5 places.
        places_input.send_keys("5")
        self.driver.find_element(
            By.CSS_SELECTOR, "button[type='submit']").click()

        self.assertIn("Booking complete: 5 places purchased.",
                      self.driver.page_source)
        self.assertIn("Points available: 8", self.driver.page_source)
        self.assertIn("Number of Places: 8", self.driver.page_source)

        # 4) The user opens the points board and checks the updated points.
        self.driver.find_element(By.LINK_TEXT, "Points Board").click()

        self.assertIn("Public Points Board", self.driver.page_source)
        simply_lift_row = self.driver.find_element(
            By.XPATH,
            "//tr[td[normalize-space()='Simply Lift']]",
        )
        self.assertIn("8", simply_lift_row.text)
