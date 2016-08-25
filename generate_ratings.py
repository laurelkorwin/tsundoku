import datetime
import random
from model import User, Book, Board, Node, Rating, Recommendation, Relationship
from boards import add_board
from model import connect_to_db, db
from tsundoku import check_for_node
from server import app

def add_boards(int1, int2):
    """Given two integers, add boards for users in that range"""

    board_name = 'My Board'
    for user in range(int1, int2):
        add_random_board(board_name, user)

def add_random_board(board_name, user_id):
    """Given board details, create new board."""

    date_created = datetime.datetime.now().strftime('%m-%d-%y')

    new_board = Board(board_name=board_name, user_id=user_id, date_created=date_created)

    db.session.add(new_board)
    db.session.commit()

def add_ratings(int1, int2):

    user_book_tuples = [(a, b) for a in range(int1, int2) for b in range(1, 22)]
    other_tuples = [(a, b) for a in range(int1, int2) for b in range(24, 394)]
    user_book_tuples += other_tuples
    current_date = datetime.datetime.now().strftime('%m-%d-%y')

    for tup in user_book_tuples:
        user_id = tup[0]
        board_id = Board.query.filter_by(user_id=user_id).first().board_id
        hasread = bool(random.getrandbits(1))
        if hasread is True:
            score = random.randint(1, 5)
        else:
            score = None
        new_rating = Rating(user_id=tup[0], book_id=tup[1], board_id=board_id, rating=score,
                        has_read=hasread, date_added=current_date)
        db.session.add(new_rating)
        db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)
