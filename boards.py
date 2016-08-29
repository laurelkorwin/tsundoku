"""BOARD SPECIFIC FUNCTIONALITY"""

from models import *
from model import *
from flask import Flask, render_template, redirect, request, flash, session, jsonify
import datetime
from tsundoku import check_for_node


def add_new_book(asin, title, author, md_image, lg_image, url, num_pages, primary_node_id, parent_node_id):
    """Given inputs, adds a new book to the database."""

    title = str(title)
    if len(title) > 100:
        title = title[0:100]

    new_book = Book(asin=asin, title=title, author=author, md_image=md_image,
                    lg_image=lg_image, url=url, num_pages=num_pages, primary_node_id=primary_node_id, parent_node_id=parent_node_id)
    db.session.add(new_book)
    db.session.commit()

def add_new_books_from_list(lst):

    for book in lst:
        new_book = Book(asin=book['ASIN'], title=book['title'], author=book['author'], md_image=book['md_image'],
                        lg_image=book['lg_image'], url=book['URL'], num_pages=book['num_pages'],
                        primary_node_id=book['primary_node_id'], parent_node_id=book['parent_node_id'])
        db.session.add(new_book)
        db.session.commit()
        add_node_primary = check_for_node(book['primary_node_id'], book['primary_node'])
        add_node_parent = check_for_node(book['parent_node_id'], book['parent_node'])


def add_rating(book_id, user_id, board, current_date, hasread, rating, notes=None):
    """Given inputs, add a new rating."""

    new_rating = Rating(book_id=book_id, user_id=user_id, board_id=board,
                        date_added=current_date, has_read=hasread, rating=rating, notes=notes)
    db.session.add(new_rating)
    db.session.commit()


def evaluate_ratings(ratings):
    """Given a list of user ratings, return a list of dictionaries with ratings info."""

    books = []

    for rating in ratings:
        rating_info = rating.evaluate_rating()
        books.append(rating_info)

    return books


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
            if rating.date_deleted is None:
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
