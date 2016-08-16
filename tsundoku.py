"""DATABASE QUERIES AND FUNCTIONS"""

from model import connect_to_db, db, User, Book, Rating, Board, Relationship, Recommendation
import datetime


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


def add_relationships(user_id, friend_id):
    """Given a user's id and the friend's user id, add two relationships to the DB."""

    current_date = datetime.datetime.now().strftime('%m-%d-%y')

    relationship_1 = Relationship(primary_friend=user_id, secondary_friend=friend_id,
                                  requesting_friend=True, status="Pending", date_initiated=current_date)
    relationship_2 = Relationship(primary_friend=friend_id, secondary_friend=user_id,
                                  requesting_friend=False, status="Pending", date_initiated=current_date)
    db.session.add_all([relationship_1, relationship_2])
    db.session.commit()

    return "Friend request sent!"





