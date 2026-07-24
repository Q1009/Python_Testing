from selenium import webdriver
from selenium.webdriver.common.by import By
from flask_testing import LiveServerTestCase
from server import create_app

class TestAuthentication(LiveServerTestCase):
    def create_app(self):
        return create_app()

    def setUp(self):
        self.driver = webdriver.Firefox()  # Ensure you have the GeckoDriver installed and in your PATH
        self.driver.get(self.get_server_url())

    def tearDown(self):
        self.driver.quit()

    def test_login_page_loads(self):
        self.driver.get(self.get_server_url())
        assert self.driver.current_url in ('http://127.0.0.1:5000/', 'http://localhost:5000/')
        self.assertIn("Welcome to the GUDLFT Registration Portal!", self.driver.page_source)

    def test_login_with_valid_credentials(self):
        email_input = self.driver.find_element(By.ID, "email")
        email_input.send_keys("john@simplylift.co")
        login_button = self.driver.find_element(By.ID, "login")
        login_button.click()
        self.assertIn("Welcome, Simply Lift", self.driver.page_source)

    def test_login_with_invalid_credentials(self):
        # 1) L'utilisateur tente de se connecter avec un identifiant non valide.
        email_input = self.driver.find_element(By.ID, "email")
        email_input.send_keys("unknown-user@gudlft.co")
        self.driver.find_element(By.ID, "login").click()

        # 2) Il est redirige vers la page d'accueil avec un message d'erreur explicite.
        self.assertIn("Welcome to the GUDLFT Registration Portal!", self.driver.page_source)
        self.assertIn("Unfortunately, the email you entered was not found.", self.driver.page_source)