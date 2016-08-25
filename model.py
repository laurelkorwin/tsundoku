
from flask_sqlalchemy import SQLAlchemy
from models import *


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



class Relationship(db.Model):
    """User relationship information"""

    __tablename__ = "relationships"

    relationship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    primary_friend = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    secondary_friend = db.Column(db.Integer, nullable=False)
    requesting_friend = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    date_initiated = db.Column(db.DateTime, nullable=False)

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

    def ignore_rec(self):
        """Mark recommendation as ignored."""

        self.status = "Ignored"
        db.session.commit()

        return self.recommendation_id


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///tsundoku'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
