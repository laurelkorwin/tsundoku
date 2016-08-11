
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Book, Rating, Board
from search import setup_API, search_API, process_result
from boards import add_board, add_new_book, add_rating, evaluate_ratings
from tsundoku import get_user_by_username, get_book_by_asin, get_board_by_userid, get_ratings_by_board_id
from login import process_new_login, process_new_registration
import datetime

app = Flask(__name__)

app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined

#ROUTES

@app.route('/')
def show_homepage():
    """Homepage"""

    return render_template("homepage.html")


@app.route('/login')
def show_login():
    """Login form"""

    return render_template('login.html')

@app.route('/process_login', methods=['POST'])
def process_login():
    """Process user log-in information."""

    username = request.form.get('username')
    password = request.form.get('password')

    user_exists = get_user_by_username(username)

    return process_new_login(user_exists, password)


@app.route('/register')
def register_user():
    """Process registration information"""

    return render_template('register.html')


@app.route('/process_registration', methods=['POST'])
def process_registration():

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    user_exists = get_user_by_username(username)

    return process_new_registration(user_exists, username, email, password)


@app.route('/search')
def search():

    search_term = request.args.get('search')

    results_list = process_result(search_API(search_term))
    user_id = session['logged_in']
    existing_boards = get_board_by_userid(user_id)

    return render_template('search_results.html', results_list=results_list, existing_boards=existing_boards)

@app.route('/add_book', methods=['POST'])
def add_book():
    """Add book to board"""

    title = request.form.get('title')                           #gets book attributes (most using hidden inputs)
    author = request.form.get('author')
    asin = request.form.get('asin')
    md_image = request.form.get('md_image')
    lg_image = request.form.get('lg_image')
    url = request.form.get('url')
    board = request.form.get('board')
    hasread = request.form.get('hasread')
    rating = request.form.get('rating')

    if hasread:
        hasread = True
    else:
        hasread = False

    user_id = session['logged_in']
    current_date = datetime.datetime.now().strftime('%m-%d-%y')

    book_exists = get_book_by_asin(asin)

    if book_exists == None:
        new_book = add_new_book(asin, title, author, md_image, lg_image, url)
        new_book_id = get_book_by_asin(asin)
        new_rating = add_rating(new_book_id, user_id, board, current_date, hasread, rating)
    else:
        current_book_id = book_exists
        new_rating = add_rating(current_book_id, user_id, board, current_date, hasread, rating)

    flash('Book successfully added!')

    return redirect('/board_details/' + board)

@app.route('/create_board')
def create_board():
    """Allows user to create a board"""

    user_id = session['logged_in']
    existing_boards = get_board_by_userid(user_id)

    return render_template("create_board.html", existing_boards=existing_boards)

@app.route('/process_board', methods=['POST'])
def process_new_board():
    """Adds new board to the database."""

    board_name = request.form.get('board_name')
    user_id = session['logged_in']

    new_board = add_board(board_name, user_id)

    return redirect('/create_board')

@app.route('/board_details/<board_id>')
def show_board_details(board_id):
    """Show books in board"""

    session['board_id'] = board_id

    ratings = get_ratings_by_board_id(board_id)
    board = Board.query.get(board_id).board_name

    books = evaluate_ratings(ratings)

    return render_template("board_details.html", books=books, board_title=board, board_id=board_id)

@app.route('/get_read_books')
def get_read_books():
    """Get books read by user ID"""

    user_id = session['logged_in']
    board_id = session['board_id']
    board = Board.query.get(board_id).board_name
    hasread = request.args.get('hasread')
    if hasread == "True":
        hasread = True
        read_books = Rating.query.filter_by(user_id=user_id, has_read=hasread, board_id=board_id).all()
    elif hasread == "False":
        hasread = False
        read_books = Rating.query.filter_by(user_id=user_id, has_read=hasread, board_id=board_id).all()
    else:
        read_books = Rating.query.filter_by(user_id=user_id, board_id=board_id).all()


    # read_books = Rating.query.filter_by(user_id=user_id, has_read=hasread, board_id=board_id).all()

    books = evaluate_ratings(read_books)

    return render_template("board_details.html", books=books, board_title=board)


@app.route('/logout')
def logout_user():
    """Logout user"""

    del session['logged_in']                                    #deletes logged in key from session
    flash("You are successfully logged out!")

    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    # app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host='0.0.0.0', debug=False, port=5000)
