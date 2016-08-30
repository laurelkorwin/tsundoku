import unittest
import server
import os
import model

# INTEGRATION TESTS

class MyAppIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = 'key'

        with self.client as c:
            with c.session_transaction() as session:
                session['logged_in'] = 1

        model.connect_to_db(app, "postgresql:///testdb")

        db.create_all()


    def test_homepage(self):

        result = self.client.get('/')

        self.assertIn('tsundoku', result.data)


if __name__ == "__main__":
    unittest.main()