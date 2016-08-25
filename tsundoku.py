"""DATABASE QUERIES AND FUNCTIONS"""

import model
import models
import datetime


def get_user_by_username(username):
    """Given a username, query database to return users."""

    result = User.query.filter_by(user_name=username).first()

    if result != None:
        return result
    else:
        return None

# These can be class methods rather than object methods
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


def check_for_node(node_id, node_name):
    """Given node id, check if node exists in DB and add it + name if it does not."""

    node_exists = Node.query.filter_by(node_id=node_id).first()
    if node_exists == None:
        new_node = Node(node_id=node_id, node_name=node_name)
        db.session.add(new_node)
        db.session.commit()

    return "Node added"

def edit_notes(rating_id, notes):
    """Given rating id and notes for a rating, update notes in DB."""

    this_rating = Rating.query.filter_by(rating_id=rating_id).first()
    this_rating.notes = notes
    db.session.commit()

    return str(this_rating.board_id)


"""RELATIONSHIPS FUNCTIONALITY"""

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


def accept_friend_db(user_id, friend_id):
    """Given a user id and a friend id, change relationship status to accepted."""

    this_relationship_1 = Relationship.query.filter_by(primary_friend=user_id, secondary_friend=friend_id).first()
    this_relationship_1.status = "Accepted"
    this_relationship_2 = Relationship.query.filter_by(primary_friend=friend_id, secondary_friend=user_id).first()
    this_relationship_2.status = "Accepted"
    db.session.commit()

    return "Accepted friend!"


def deny_friend_db(user_id, friend_id):
    """Given a user id and a friend id, change relationship status to denied."""

    this_relationship_1 = Relationship.query.filter_by(primary_friend=user_id, secondary_friend=friend_id).first()
    this_relationship_1.status = "Denied"
    this_relationship_2 = Relationship.query.filter_by(primary_friend=friend_id, secondary_friend=user_id).first()
    this_relationship_2.status = "Denied"
    db.session.commit()

    return "Denied friend."

def get_current_friends(user_id):
    """Given a user ID, get current friends from DB."""

    current = Relationship.query.filter_by(primary_friend=user_id, status="Accepted").all()

    friend_info = [(friend.get_secondary_friend_info().user_name, friend.secondary_friend) for friend in current]

    return friend_info

def get_current_recs(user_id):
    """Given user ID, get current recommendations from the DB."""

    current_recs = Recommendation.query.filter_by(referring_user=user_id).all()

    my_recs = [(recommendation.book_id, recommendation.referred_user) for recommendation in current_recs]

    return my_recs

def return_relationship_id(primary_friend, secondary_friend):
    """Given two user ids, return a relationship ID"""

    your_relationship = db.session.query(Relationship.relationship_id).filter(Relationship.primary_friend == primary_friend, Relationship.secondary_friend == secondary_friend).first()

    return your_relationship[0]

def add_recommendation(relationship_id, user_id, friend_id, book_id, comment, status="Pending"):
    """Creates new recommendation in DB."""

    recommendation = Recommendation(relationship_id=relationship_id, referring_user=user_id, referred_user=friend_id, book_id=book_id, comments=comment, status=status)
    db.session.add(recommendation)
    db.session.commit()

    return "Recommendation made!"

def ignore_rec_db(rec_id):
    """Given recommendation ID, changes status to 'ignored'"""

    this_rec = Recommendation.query.filter_by(recommendation_id=rec_id).first()
    this_rec.status = "Ignored"
    db.session.commit()

    return this_rec.recommendation_id
