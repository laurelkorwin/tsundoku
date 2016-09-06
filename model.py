
from flask_sqlalchemy import SQLAlchemy
from models import *
import datetime
from collections import defaultdict


# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

#MODEL DEFINITIONS GO HERE


class User(db.Model):
    """Users of app"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)

    userrels = db.relationship('Relationship', backref=db.backref('users'))

    def __repr__(self):
        """Return user data in a better format"""

        return "<User User ID: {}, Username: {}, User email: {}>".format(self.user_id,
                                                                  self.user_name,
                                                                  self.email)

    @classmethod
    def get_user_by_username(cls, username):
        """Given a username, query database to return user object."""

        result = User.query.filter_by(user_name=username).first()

        return result


class Node(db.Model):
    """Amazon product node information"""

    __tablename__ = "nodes"

    node_id = db.Column(db.String(100), primary_key=True)
    node_name = db.Column(db.String(100), nullable=False)


class Board(db.Model):
    """Board information"""

    __tablename__ = "boards"

    board_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    board_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    published = db.Column(db.Boolean, nullable=False, default=False)
    date_created = db.Column(db.DateTime, nullable=False)

    userbd = db.relationship('User', backref=db.backref('users', order_by=user_id))

    def __repr__(self):
        """Return board data in a better format."""

        return "<Board Board ID: {}, Board name: {}, User ID: {}>".format(self.board_id,
                                                                   self.board_name,
                                                                   self.user_id)

    @classmethod
    def get_board_by_userid(cls, user_id):
        """Given a user ID, query database to return any boards."""

        result = Board.query.filter_by(user_id=user_id).all()

        return result

    @classmethod
    def add_board(cls, board_name, user_id):
        """Given board details, create new board."""

        date_created = datetime.datetime.now().strftime('%m-%d-%y')

        new_board = Board(board_name=board_name, user_id=user_id, date_created=date_created)

        db.session.add(new_board)
        db.session.commit()

        return "Your board successfully created!"


class Book(db.Model):
    """Books saved by users"""

    __tablename__ = "books"

    book_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    asin = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100))
    md_image = db.Column(db.String(200))
    lg_image = db.Column(db.String(200))
    url = db.Column(db.String(400))
    num_pages = db.Column(db.Integer, nullable=True)
    primary_node_id = db.Column(db.String(100), db.ForeignKey('nodes.node_id'), nullable=True)
    parent_node_id = db.Column(db.String(100), db.ForeignKey('nodes.node_id'), nullable=True)
    date_added = db.Column(db.DateTime, nullable=True)

    primnodebk = db.relationship('Node', foreign_keys=[primary_node_id])
    parnodebk = db.relationship('Node', foreign_keys=[parent_node_id])

    def __repr__(self):
        """Return book data in a better format"""

        return "<Book Book ID: {}, ASIN: {}, Title: {}, Author: {}>".format(self.book_id,
                                                                    self.asin, self.title,
                                                                    self.author)

    @classmethod
    def get_book_by_asin(cls, ASIN):
        """Given ASIN, return book."""

        result = Book.query.filter_by(asin=ASIN).first()

        if result != None:
            return result.book_id
        else:
            return None


class Rating(db.Model):
    """Rating information for each book/user"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    board_id = db.Column(db.Integer, db.ForeignKey('boards.board_id'))
    rating = db.Column(db.Integer, nullable=True)
    has_read = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, nullable=False)
    date_deleted = db.Column(db.DateTime, nullable=True)

    userrtg = db.relationship('User', backref=db.backref('ratings', order_by=rating_id))
    book = db.relationship('Book', backref=db.backref('ratings', order_by=rating_id))
    board = db.relationship('Board', backref=db.backref('ratings', order_by=rating_id))

    def __repr__(self):
        """Return ratings data in a better format"""

        return "<Rating Rating ID: {}, Book ID: {}, User ID: {}, Board ID: {}>".format(
                                                                                self.rating_id,
                                                                                self.book_id,
                                                                                self.user_id,
                                                                                self.board_id)

    @classmethod
    def get_ratings_by_board_id(cls, board_id):
        """Given a board ID, return ratings information."""

        result = Rating.query.filter_by(board_id=board_id).all()

        return result

    @classmethod
    def get_average_scores(cls, user_id):

        ratings = Rating.query.filter(Rating.user_id == user_id, Rating.rating != None).all()

        scores = {}

        for rating in ratings:
            node_name = rating.book.parnodebk.node_name
            score = rating.rating
            if node_name not in scores:
                scores[node_name] = defaultdict(int)
            scores[node_name]['counter'] += 1
            scores[node_name]['sum_score'] += score
            scores[node_name]['avg'] = float(scores[node_name]['sum_score']) / scores[node_name]['counter']

        return scores

    @classmethod
    def get_num_pages(cls, user_id):

        ratings = Rating.query.filter_by(user_id=user_id, has_read=True).all()

        our_data = defaultdict(int)

        for rating in ratings:
            node_name = rating.book.parnodebk.node_name
            num_pages = int(rating.book.num_pages)
            our_data[node_name] += num_pages

        return our_data

    def update_notes(self, notes):
        """Given notes for a rating, update notes in DB."""

        self.notes = notes
        db.session.commit()
        return self.board_id

    def mark_read(self):
        """Mark book as read in DB"""

        self.has_read = True
        db.session.commit()

        return "Marked this book as read!"

    def update_rating(self, score):
        """Given new score, update book rating"""

        asin = self.book.asin
        self.rating = score
        db.session.commit()

        return asin

    def evaluate_rating(self):
        """Return userful information in dictionary format"""

        rating_id = self.rating_id
        asin = self.book.asin
        book_id = self.book_id
        title = self.book.title
        author = self.book.author
        md_image = self.book.md_image
        lg_image = self.book.lg_image
        url = self.book.url
        hasread = self.has_read
        notes = self.notes
        rating = self.rating
        date_deleted = self.date_deleted
        if notes is None:
            notes = ''
        rating_info = {'title': title, 'author': author, 'md_image': md_image, 'url': url,
                      'hasread': hasread, 'rating_id': rating_id, 'rating': rating, 'book_id': book_id,
                      'asin': asin, 'lg_image': lg_image, 'notes': notes, 'date_deleted': date_deleted}

        return rating_info


class Relationship(db.Model):
    """User relationship information"""

    __tablename__ = "relationships"

    relationship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    primary_friend = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    secondary_friend = db.Column(db.Integer, nullable=False)
    requesting_friend = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    date_initiated = db.Column(db.DateTime, nullable=False)

    @classmethod
    def get_current_friends(cls, user_id):
        """Given user id, return a list of tuples of friend info"""
        current = Relationship.query.filter_by(primary_friend=user_id, status="Accepted").all()

        friend_info = [(friend.get_secondary_friend_info().user_name, friend.secondary_friend) for friend in current]

        return friend_info

    def get_secondary_friend_info(self):
        """Query database for secondary friend info"""

        secondary_friend = self.secondary_friend

        secondary_friend_info = User.query.get(secondary_friend)

        return secondary_friend_info

    def deny(self):
        """Mark relationship status as denied"""

        self.status = "Denied"
        db.session.commit()

        return "Denied friend."

    def accept(self):
        """Mark relationship status as accepted"""

        self.status = "Accepted"
        db.session.commit()

        return "Accepted friend!"


class Recommendation(db.Model):
    """User to user recommendation info"""

    __tablename__ = "recommendations"

    recommendation_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    relationship_id = db.Column(db.Integer, db.ForeignKey('relationships.relationship_id'))
    referring_user = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    referred_user = db.Column(db.Integer)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    status = db.Column(db.String(20), nullable=False)
    comments = db.Column(db.Text)

    relation = db.relationship('Relationship', backref=db.backref('recommendations'))
    users = db.relationship('User', backref=db.backref('recommendations'))
    bookinfo = db.relationship('Book', backref=db.backref('recommendations'))

    @classmethod
    def get_current_recs_referring(cls, user_id, book_id):
        """Given user ID, get current recommendations from the DB where you referred the book."""

        current_recs = Recommendation.query.filter_by(referring_user=user_id, book_id=book_id).all()

        # list of users you've already recommended the book to
        my_recs = [recommendation.referred_user for recommendation in current_recs]

        return my_recs

    @classmethod
    def get_current_recs_referred(cls, user_id):
        """Given user ID, get current recs from the DB where you are the referred user."""

        recs_for_me = Recommendation.query.filter_by(referred_user=user_id, status="Pending").all()

        rec_dict = {}

        for rec in recs_for_me:
            rec_dict[rec.recommendation_id] = {'book_id': rec.book_id, 'referring_user_id': rec.referring_user,
                                           'referring_user': rec.users.user_name, 'title': rec.bookinfo.title,
                                           'author': rec.bookinfo.author, 'md_image': rec.bookinfo.md_image,
                                           'lg_image': rec.bookinfo.lg_image, 'comment': rec.comments}
        return rec_dict

    @classmethod
    def get_all_recs_referred(cls, user_id):
        """Given user ID, get all recs for that user and return totals of each status."""

        recs_for_me = db.session.query(Recommendation.recommendation_id, Recommendation.status).filter_by(referred_user=user_id).all()

        sum_dict = defaultdict(int)

        for rec in recs_for_me:
            status = rec.status
            if status == "Accepted":
                sum_dict["Accepted"] += 1
            elif status == "Ignored":
                sum_dict["Ignored"] += 1
            else:
                sum_dict["Pending"] += 1

        return sum_dict

    @classmethod
    def get_most_trusted(cls, user_id):
        """Given user id, return dict with friend and rec info"""

        recs_for_me = Recommendation.query.filter_by(referred_user=user_id).all()

        rec_dict = {}

        for rec in recs_for_me:
            user_name = User.query.get(rec.referring_user).user_name
            if user_name not in rec_dict:
                rec_dict[user_name] = {'total': 0, 'accepted': 0, 'percent_accepted': 0.0}
            rec_dict[user_name]['total'] += 1
            if rec.status == "Accepted":
                rec_dict[user_name]['accepted'] += 1
            rec_dict[user_name]['percent_accepted'] = (float(rec_dict[user_name]['accepted']) / rec_dict[user_name]['total']) * 100

        return rec_dict

    def ignore_rec(self):
        """Mark recommendation as ignored."""

        self.status = "Ignored"
        db.session.commit()

        return self.recommendation_id


##############################################################################
# Helper functions

def connect_to_db(app, config='postgresql:///tsundoku'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = config
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
