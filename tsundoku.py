"""DATABASE QUERIES AND FUNCTIONS"""

from model import connect_to_db, db, User, Book, Rating, Board
from collections import defaultdict


def get_user_by_username(username):
    """Given a username, query database to return users."""

    result = User.query.filter_by(user_name=username).first()

    if result != None:
        return result
    else:
        return None


def get_book_by_asin(asin):
    """Given a book ASIN, query database to return books."""

    result = Book.query.filter_by(asin=asin).first()

    if result != None:
        return result.book_id
    else:
        return None


def get_board_by_userid(user_id):
    """Given a user ID, query database to return any boards."""

    result = Board.query.filter_by(user_id=user_id).all()

    return result


def get_ratings_by_board_id(board_id):
    """Given a board ID, return ratings information."""

    result = Rating.query.filter_by(board_id=board_id).all()

    return result





