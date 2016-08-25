"""DATABASE QUERIES AND FUNCTIONS"""
from models import *
from model import *
import datetime

# These can be class methods rather than object methods

def check_for_node(node_id, node_name):
    """Given node id, check if node exists in DB and add it + name if it does not."""

    node_exists = Node.query.filter_by(node_id=node_id).first()
    if node_exists == None:
        new_node = Node(node_id=node_id, node_name=node_name)
        db.session.add(new_node)
        db.session.commit()

    return "Node added"


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
