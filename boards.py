"""BOARD SPECIFIC FUNCTIONALITY"""

from model import connect_to_db, db, User, Book, Rating, Board
from flask import Flask, render_template, redirect, request, flash, session, jsonify
import datetime


def add_board(board_name, user_id):
    """Given board details, create new board."""

    date_created = datetime.datetime.now().strftime('%m-%d-%y')

    new_board = Board(board_name=board_name, user_id=user_id, date_created=date_created)

    db.session.add(new_board)
    db.session.commit()
    flash("Your board successfully created!")

def add_new_book(asin, title, author, md_image, lg_image, url):
    """Given inputs, adds a new book to the database."""

    new_book = Book(asin=asin, title=title, author=author, md_image=md_image,
                    lg_image=lg_image, url=url)
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
        book_id = rating.book_id
        title = rating.book.title
        author = rating.book.author
        md_image = rating.book.md_image
        url = rating.book.url
        hasread = rating.has_read
        rating = rating.rating
        books.append({'title': title, 'author': author, 'md_image': md_image, 'url': url,
                      'hasread': hasread, 'rating': rating, 'book_id': book_id})

    return books

def mark_read(user_id, book_id):
    """Given a user ID and Book ID, mark the book as read for that user."""

    this_rating = Rating.query.filter_by(user_id=user_id, book_id=book_id).first()
    this_rating.has_read = True
    db.session.commit()

    return "Marked this book as read!"
