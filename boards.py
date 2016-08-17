"""BOARD SPECIFIC FUNCTIONALITY"""

from model import connect_to_db, db, User, Book, Rating, Board, Relationship, Recommendation
from flask import Flask, render_template, redirect, request, flash, session, jsonify
import datetime


def add_board(board_name, user_id):
    """Given board details, create new board."""

    date_created = datetime.datetime.now().strftime('%m-%d-%y')

    new_board = Board(board_name=board_name, user_id=user_id, date_created=date_created)

    db.session.add(new_board)
    db.session.commit()

    flash("Your board successfully created!")


def add_new_book(asin, title, author, md_image, lg_image, url, num_pages, primary_node_id, parent_node_id):
    """Given inputs, adds a new book to the database."""

    new_book = Book(asin=asin, title=title, author=author, md_image=md_image,
                    lg_image=lg_image, url=url, num_pages=num_pages, primary_node_id=primary_node_id, parent_node_id=parent_node_id)
    db.session.add(new_book)
    db.session.commit()


def add_rating(book_id, user_id, board, current_date, hasread, rating):
    """Given inputs, add a new rating."""

    new_rating = Rating(book_id=book_id, user_id=user_id, board_id=board,
                        date_added=current_date, has_read=hasread, rating=rating)
    db.session.add(new_rating)
    db.session.commit()


def evaluate_ratings(ratings):
    """Given a list of user ratings, return a list of dictionaries with ratings info."""

    books = []

    for rating in ratings:
        rating_id = rating.rating_id
        asin = rating.book.asin
        book_id = rating.book_id
        title = rating.book.title
        author = rating.book.author
        md_image = rating.book.md_image
        lg_image = rating.book.lg_image
        url = rating.book.url
        hasread = rating.has_read
        rating = rating.rating
        books.append({'title': title, 'author': author, 'md_image': md_image, 'url': url,
                      'hasread': hasread, 'rating_id': rating_id, 'rating': rating, 'book_id': book_id,
                      'asin': asin, 'lg_image': lg_image})

    return books


def mark_read(user_id, book_id):
    """Given a user ID and Book ID, mark the book as read for that user."""

    this_rating = Rating.query.filter_by(user_id=user_id, book_id=book_id).first()
    this_rating.has_read = True
    db.session.commit()

    return "Marked this book as read!"


def update_book_rating(user_id, book_id, score):
    """Given a user ID, book ID and score, rate the book in the DB."""

    this_rating = Rating.query.filter_by(user_id=user_id, book_id=book_id).first()
    asin = this_rating.book.asin
    this_rating.rating = score
    db.session.commit()

    return asin


def get_bd_imgs(lst):
    """Takes in a list of tuples (of board id and board name).
       Returns a dictionary w/key of tuple and value of list of image urls
       for that board."""

    my_dict = {}

    for item in lst:
        board_id = item[0]
        my_dict[item] = []
        ratings = Rating.query.filter_by(board_id=board_id)
        for rating in ratings:
            md_image = rating.book.md_image
            my_dict[item].append(md_image)

    return my_dict


def filter_by_read(hasread, user_id, board_id):
    """Given variable for hasread, user id and board id return a list of book objects"""

    if hasread == "True":
        hasread = True
        read_books = Rating.query.filter_by(user_id=user_id, has_read=hasread, board_id=board_id).all()
    elif hasread == "False":
        hasread = False
        read_books = Rating.query.filter_by(user_id=user_id, has_read=hasread, board_id=board_id).all()
    else:
        read_books = Rating.query.filter_by(user_id=user_id, board_id=board_id).all()

    return read_books
