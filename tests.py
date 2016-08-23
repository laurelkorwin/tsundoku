from selenium import webdriver
import unittest
import server
import os

# SELENIUM TESTS
class TestHomepage(unittest.TestCase):
    """Tests homepage"""

    def setUp(self):
        chromedriver = "/Users/laurelkorwin/src/project/lenv/chromedriver"
        os.environ['webdriver.chrome.driver'] = chromedriver
        self.browser = webdriver.Chrome(chromedriver)

    def tearDown(self):
        self.browser.quit()

    def test_title(self):
        self.browser.get('http://localhost:5000/')
        self.assertEqual(self.browser.title, 'tsundoku')

class TestLoginFunction(unittest.TestCase):
    """Tests that login function works with sample user info."""

    def setUp(self):
        chromedriver = "/Users/laurelkorwin/src/project/lenv/chromedriver"
        os.environ['webdriver.chrome.driver'] = chromedriver
        self.browser = webdriver.Chrome(chromedriver)

    def tearDown(self):
        self.browser.quit()

    def test_login(self):
        self.browser.get('http://localhost:5000/login')

        username = self.browser.find_element_by_id('username_field')
        username.send_keys("sample")

        password = self.browser.find_element_by_id('password_field')
        password.send_keys("abc123")

        btn = self.browser.find_element_by_id('login')
        btn.click()

        result = self.browser.find_element_by_class_name('flashes').text
        self.assertIn(result, "Successfully logged in!")

# OTHER TESTS

if __name__ == "__main__":
    unittest.main()