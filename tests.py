import unittest
import server
import os
import model
import search

# INTEGRATION TESTS

class BasicTest(unittest.TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = 'key'


    def test_homepage(self):

        result = self.client.get('/')

        self.assertIn('tsundoku', result.data)

    def test_login(self):

        result = self.client.get('/login')

        self.assertIn('Username', result.data)
        self.assertNotIn('Logout', result.data)


class UserLoggedIn(unittest.TestCase):

    def setUp(self):
        """Stuff to do before every test."""

        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = 'key'

        with self.client as c:
            with c.session_transaction() as session:
                session['logged_in'] = 1

        model.connect_to_db(server.app, "postgresql:///testdb")

        model.db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        model.db.session.close()

    def testDisplay(self):

        result = self.client.get('/')

        self.assertIn('Boards', result.data)
        self.assertNotIn('Register', result.data)

    def testSearch(self):

        my_search = search.search_API('harry potter')

        processed_search = search.process_result(my_search)

        first_result = processed_search[0]

        self.assertIn('title', first_result.keys())
        self.assertIn('Harry Potter', str(first_result['title']))

    def testReturnFirst(self):

        my_search = search.search_API('harry potter')

        regular_processed_search = search.process_result(my_search)
        first_item = regular_processed_search[0]

        first_result_search = search.return_first_result(my_search)

        self.assertEqual(first_item['title'], first_result_search['title'])


class TestEvaluationFunctions(unittest.TestCase):

    def setUp(self):
        """Stuff to do before every test."""

        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = 'key'

        with self.client as c:
            with c.session_transaction() as session:
                session['logged_in'] = 1

        model.connect_to_db(server.app, "postgresql:///testdb")

        model.db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        model.db.session.close()

    def testEvaluation(self):

        my_user_id = 1

        my_rating_example = model.Rating.query.filter_by(user_id=my_user_id).first()

        result = my_rating_example.evaluate_rating().keys()

        self.assertIn('title', result)
        self.assertIn('md_image', result)


if __name__ == "__main__":
    unittest.main()