"""FRIEND FUNCTIONALITY"""

from model import *
import models

def return_potential_friends(user_id, friend_term):
    """Given user's id and a search term, returns list of potential friend objects"""

    if '@' in friend_term:
        potentials = db.session.query(User).filter(User.email.like("{}%".format(friend_term)), User.user_id != user_id).all()
        query = db.session.query(Relationship.secondary_friend).filter(Relationship.primary_friend == user_id).all()
        existing_relationships = [item[0] for item in query]
        possible_friends = [friend for friend in potentials if friend.user_id not in existing_relationships]
    else:
        potentials = db.session.query(User).filter(User.user_name.like("{}%".format(friend_term)), User.user_id != user_id).all()
        query = db.session.query(Relationship.secondary_friend).filter(Relationship.primary_friend == user_id).all()
        existing_relationships = [item[0] for item in query]
        possible_friends = [friend for friend in potentials if friend.user_id not in existing_relationships]

    return possible_friends


def make_friend_dict(friend_list):
    """Given list of potential friend objects, returns a dictionary of friend info."""

    potential_friend_dict = {}

    for friend in friend_list:
        potential_friend_dict[friend.user_id] = friend.user_name

    return potential_friend_dict
