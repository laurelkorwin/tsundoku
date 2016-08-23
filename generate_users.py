from model import User, Book, Board, Node, Rating, Recommendation, Relationship
from model import connect_to_db, db
from server import app
import requests

def get_user_data():
    """Get user data from random user API"""

    data = requests.get('http://api.randomuser.me/?results=100')

    my_dict = data.json()

    return my_dict

def process_data(dct):
    """Given dict of user data, extract necessary info"""

    results = dct['results']

    users = [(item['login']['username'], item['login']['password'], item['email']) for item in results]

    return users

def add_to_db(users):
    """Given list of dicts of user info, add users to DB"""

    for user in users:
        username = user[0]
        password = user[1]
        email = user[2]
        new_user = User(user_name=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    return "Finished adding users."

if __name__ == "__main__":
    connect_to_db(app)

data = get_user_data()

processed_data = process_data(data)

add_to_db(processed_data)
