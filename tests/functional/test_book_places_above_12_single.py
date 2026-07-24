from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from server import create_app


class TestBookPlacesAbove12Single(LiveServerTestCase):
	def create_app(self):
		return create_app()

	def setUp(self):
		self.driver = webdriver.Firefox()  # Ensure GeckoDriver is installed and in PATH.
		self.driver.get(self.get_server_url())

	def tearDown(self):
		self.driver.quit()

	def test_user_cannot_book_thirteen_places_in_one_request(self):
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

		# 3) The user tries to buy 13 places in one request.
		# Force the invalid value through the form to validate server-side guard.
		self.driver.execute_script(
			"arguments[0].removeAttribute('max'); arguments[0].value = '13';",
			places_input,
		)
		self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

		# 4) The request is rejected and points/places remain unchanged.
		self.assertIn("You cannot book more than 12 places per competition.", self.driver.page_source)
		self.assertIn("Points available: 13", self.driver.page_source)
		self.assertIn("Number of Places: 13", self.driver.page_source)
