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

    def testLogin(self):
        self.browser.get('http://localhost:5000/login')

        username = self.browser.find_element_by_id('username_field')
        username.send_keys("sample")

        password = self.browser.find_element_by_id('password_field')
        password.send_keys("abc123")

        btn = self.browser.find_element_by_id('login')
        btn.click()

        result = self.browser.find_element_by_class_name('flashes').text
        self.assertIn("Successfully logged in!", result)

class TestSearch(unittest.TestCase):
    """Tests search fields with various inputs"""

    def setUp(self):
        chromedriver = "/Users/laurelkorwin/src/project/lenv/chromedriver"
        os.environ['webdriver.chrome.driver'] = chromedriver
        self.browser = webdriver.Chrome(chromedriver)

        self.browser.get('http://localhost:5000/login')

        username = self.browser.find_element_by_id('username_field')
        username.send_keys("sample")

        password = self.browser.find_element_by_id('password_field')
        password.send_keys("abc123")

        btn = self.browser.find_element_by_id('login')
        btn.click()

    def tearDown(self):
        self.browser.quit()

    def testRandomSearch(self):
        """Tests search with item not available from API"""

        self.browser.get('http://localhost:5000/')
        search_box = self.browser.find_element_by_name("search")
        search_box.send_keys("asdjf")
        btn = self.browser.find_element_by_id('search_btn')
        btn.click()

        result = self.browser.find_element_by_class_name('flashes').text
        self.assertIn("Please try again", result)

    def testRegularSearch(self):
        """Tests search with item available from API"""

        self.browser.get('http://localhost:5000/')
        search_box = self.browser.find_element_by_name("search")
        search_box.send_keys("harry potter")
        btn = self.browser.find_element_by_id('search_btn')
        btn.click()

        result = self.browser.find_element_by_class_name('container-fluid').text
        self.assertIn("Harry Potter", result)


if __name__ == "__main__":
    unittest.main()