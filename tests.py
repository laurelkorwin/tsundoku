import unittest
import server
import os
import model
import search
import friends
import json

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

    def test_register(self):

        result = self.client.get('register')

        self.assertIn('Email', result.data)


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

    def testBoardPage(self):

        my_user_id = 1

        result = self.client.get('/create_board')

        sample_board_title = model.Board.query.filter_by(user_id=my_user_id).first().board_name

        self.assertIn('Create New Board', result.data)
        self.assertIn(sample_board_title, result.data)


class SearchFunctions(unittest.TestCase):

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

class TestChartRoutes(unittest.TestCase):

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

    def testCharts(self):

        chart_1 = self.client.get('/most_trusted_data.json')
        chart_2 = self.client.get('/basic_rec_data.json')
        chart_3 = self.client.get('/avg_ratings.json')
        chart_4 = self.client.get('/pages_data.json')

        chart_1_python = json.loads(chart_1.data)
        chart_2_python = json.loads(chart_2.data)
        chart_3_python = json.loads(chart_3.data)
        chart_4_python = json.loads(chart_4.data)

        # tests that routes return anything
        self.assertIn('backgroundColor', chart_1.data)
        self.assertIn('backgroundColor', chart_2.data)
        self.assertIn('backgroundColor', chart_3.data)
        self.assertIn('backgroundColor', chart_4.data)

        # tests that there is data

        self.assertIsNotNone(chart_1_python['datasets'][0]['data'])
        self.assertIsNotNone(chart_2_python['datasets'][0]['data'])
        self.assertIsNotNone(chart_3_python['datasets'][0]['data'])
        self.assertIsNotNone(chart_4_python['datasets'][0]['data'])


class TestRecommendationFunctions(unittest.TestCase):

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

    def testIgnoreRec(self):

        user_id = 1

        random_rec = model.Recommendation.query.filter_by(referred_user=user_id).first()

        rec_id = random_rec.ignore_rec()

        random_rec_2 = model.Recommendation.query.filter_by(recommendation_id=rec_id).first()

        self.assertEqual('Ignored', random_rec_2.status)

    def testMostTrusted(self):

        user_id = 1

        most_trusted = model.Recommendation.get_most_trusted(user_id)

        self.assertIn('percent_accepted', most_trusted.values()[0].keys())


class TestFriendSearch(unittest.TestCase):

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

    def testFriendFinder(self):

        user_id = 1

        friend_term = '@'

        other_term = 'b'

        result1 = friends.return_potential_friends(user_id, friend_term)
        result2 = friends.return_potential_friends(user_id, other_term)

        self.assertIsInstance(result1, list)
        self.assertIsInstance(result2, list)

    def testFriendDictMaker(self):

        user_id = 1

        friend_term = '@'

        my_results = friends.return_potential_friends(user_id, friend_term)

        my_processed_results = friends.make_friend_dict(my_results)

        self.assertIsInstance(my_processed_results, dict)



if __name__ == "__main__":
    unittest.main()
