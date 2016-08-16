
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Book, Rating, Board, Relationship, Recommendation
from search import setup_API, search_API, process_result
from boards import add_board, add_new_book, add_rating, evaluate_ratings, mark_read, update_book_rating
from tsundoku import get_user_by_username, get_book_by_asin, get_board_by_userid, get_ratings_by_board_id, add_relationships, accept_friend_db, deny_friend_db
from login import process_new_login, process_new_registration
from friends import return_potential_friends, make_friend_dict
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

    #queries the database for user based on username
    user_exists = get_user_by_username(username)

    #processes login with user object and entered password (see login.py)
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

    #queries the database for user based on username
    user_exists = get_user_by_username(username)

    #processes registration with user object, and entered info (see login.py)
    return process_new_registration(user_exists, username, email, password)


@app.route('/search')
def search():

    search_term = request.args.get('search')

    #gets and processes search results from Amazon API (see search.py)
    results_list = process_result(search_API(search_term, 1))

    #using session key, gets the boards for the logged-in user
    user_id = session['logged_in']
    existing_boards = get_board_by_userid(user_id)

    #renders search template with the results list from API call. Allows user to click a modal window and add a book to a board.
    return render_template('search_results.html', results_list=results_list, existing_boards=existing_boards)

@app.route('/add_book', methods=['POST'])
def add_book():
    """Add book to board"""

    #hidden form inputs
    title = request.form.get('title')
    author = request.form.get('author')
    asin = request.form.get('asin')
    md_image = request.form.get('md_image')
    lg_image = request.form.get('lg_image')
    url = request.form.get('url')
    #user form inputs
    board = request.form.get('board')
    hasread = request.form.get('hasread')
    rating = request.form.get('rating')

    #reads toggle input and assigns a value to hasread accordingly
    if hasread:
        hasread = True
    else:
        hasread = False

    #gets user id from session key
    user_id = session['logged_in']
    #gets current date and formats it in a string
    current_date = datetime.datetime.now().strftime('%m-%d-%y')

    #queries the database for book based on asin
    book_exists = get_book_by_asin(asin)

    #if the book isn't in the database, adds both book and rating to the database
    #otherwise, uses the book id for the book currently in the db and creates a new rating
    if book_exists == None:
        new_book = add_new_book(asin, title, author, md_image, lg_image, url)
        new_book_id = get_book_by_asin(asin)
        new_rating = add_rating(new_book_id, user_id, board, current_date, hasread, rating)
    else:
        current_book_id = book_exists
        new_rating = add_rating(current_book_id, user_id, board, current_date, hasread, rating)

    flash('Book successfully added!')

    #redirects to the board details page (should now show recently added book)
    return redirect('/board_details/' + board)

@app.route('/create_board')
def create_board():
    """Allows user to create a board"""

    user_id = session['logged_in']
    existing_boards = get_board_by_userid(user_id)
    existing_board_ids_names = [(board.board_id, board.board_name) for board in existing_boards]

    my_dict = {}

    for item in existing_board_ids_names:
        board_id = item[0]
        my_dict[item] = []
        ratings = Rating.query.filter_by(board_id=board_id)
        for rating in ratings:
            md_image = rating.book.md_image
            my_dict[item].append(md_image)

    # simple form input allowing user to specify a new board name
    return render_template("create_board.html", existing_boards=existing_boards, my_dict=my_dict)

@app.route('/process_board', methods=['POST'])
def process_new_board():
    """Adds new board to the database."""

    board_name = request.form.get('board_name')
    user_id = session['logged_in']

    #given the board name chosen by the user, adds a new board to the DB (see boards.py)
    new_board = add_board(board_name, user_id)

    #redirects to the boards page (should now show recently added board)
    return redirect('/create_board')

@app.route('/board_details/<board_id>', methods=['POST', 'GET'])
def show_board_details(board_id):
    """Show books in board"""

    #sets session key to board id when page is visited
    session['board_id'] = board_id

    #gets ratings for that board, as well as board name
    ratings = get_ratings_by_board_id(board_id)
    board = Board.query.get(board_id).board_name

    #goes through the list of ratings and unpacks them into variables (see boards.py)
    books = evaluate_ratings(ratings)

    #renders template showing books currently on the board
    return render_template("board_details.html", books=books, board_title=board, board_id=board_id)

@app.route('/get_read_books')
def get_read_books():
    """Get books read by user ID"""

    user_id = session['logged_in']
    board_id = session['board_id']
    board = Board.query.get(board_id).board_name

    #gets desired filter from argument passed in route
    hasread = request.args.get('hasread')

    #sets variable hasread according to route input, and returns a list of objects
    #either of read books, unread books, or all books
    if hasread == "True":
        hasread = True
        read_books = Rating.query.filter_by(user_id=user_id, has_read=hasread, board_id=board_id).all()
    elif hasread == "False":
        hasread = False
        read_books = Rating.query.filter_by(user_id=user_id, has_read=hasread, board_id=board_id).all()
    else:
        read_books = Rating.query.filter_by(user_id=user_id, board_id=board_id).all()

    #goes through the list of ratings and unpacks them into variables (see boards.py)
    books = evaluate_ratings(read_books)

    #renders board details template again with filtered books
    return render_template("board_details.html", books=books, board_title=board)

@app.route('/read_book', methods=['POST'])
def mark_book_as_read():

    user_id = session['logged_in']

    #gets book id from JS post request
    book_id = request.form.get('book_id')

    #sets a message based on calling the "mark read" function that marks book read in the DB (see boards.py)
    message = mark_read(user_id, book_id)

    #sets a dictionary of results to pass back to JS
    results = {'book_id': book_id, 'message': message}

    #returns jsonified dictionary of results dict
    return jsonify(results)

@app.route('/rate_book', methods=['POST'])
def rate_book():

    user_id = session['logged_in']

    #gets book id and score from JS post request (score is user input in form)
    book_id = request.form.get('book_id')
    score = request.form.get('score')

    #updates book rating (see boards.py) and returns asin of book
    asin = update_book_rating(user_id, book_id, score)

    #returns asin and score in a dictionary to pass back to JS
    results = {'asin': asin, 'score': score}

    #returns jsonified dictionary of results dict
    return jsonify(results)


@app.route('/find_friends')
def friend_search():

    #gets user id from session, and searches database for any current pending relationships to display
    #NOTE - where user is requester.
    user_id = session['logged_in']

    pending_relationships = Relationship.query.filter_by(primary_friend=user_id, status="Pending", requesting_friend=True).all()

    #gets secondary friend info for each relationship in pending relationships
    secondary_friends = [(relationship.get_secondary_friend_info().user_name, relationship.relationship_id, relationship.status) for relationship in pending_relationships]

    my_pending_requests = Relationship.query.filter_by(secondary_friend=user_id, status="Pending", requesting_friend=True).all()

    requester_info = [(relationship.users.user_name, relationship.primary_friend, relationship.status) for relationship in my_pending_requests]

    current = Relationship.query.filter_by(primary_friend=user_id, status="Accepted").all()

    current_friends = [(friend.get_secondary_friend_info().user_name, friend.secondary_friend) for friend in current]

    #renders search page along with any pending relationships, as defined above.
    return render_template('find_friends.html', pending_relationships=secondary_friends, pending_requests=requester_info, current_friends=current_friends)


@app.route('/search_friends')
def search_friends():

    #gets search term from search form, and user id from session
    friend = request.args.get('search')
    user_id = session['logged_in']

    #gets a dictionary of potential friend info from two functions in friends file
    possible_friends = make_friend_dict(return_potential_friends(user_id, friend))

    return render_template('possible_friends.html', friends=possible_friends)


@app.route('/add_friend/<friend_id>', methods=['POST', 'GET'])
def add_friend(friend_id):

    user_id = session['logged_in']
    friend_user_id = friend_id

    added_message = add_relationships(user_id, friend_user_id)

    flash(added_message)

    return redirect("/find_friends")

@app.route('/accept_friend/<friend_id>', methods=['POST', 'GET'])
def accept_friend(friend_id):

    user_id = session['logged_in']

    accept_message = accept_friend_db(user_id, friend_id)

    flash(accept_message)

    return redirect('/find_friends')


@app.route('/deny_friend/<friend_id>', methods=['POST', 'GET'])
def deny_friend(friend_id):

    user_id = session['logged_in']

    deny_message = deny_friend_db(user_id, friend_id)

    flash(deny_message)

    return redirect('/find_friends')

@app.route('/friend_boards/<friend_id>', methods=['POST', 'GET'])
def show_friend_boards(friend_id):

    friend_boards = get_board_by_userid(friend_id)
    friend_name = User.query.get(friend_id).user_name
    friend_board_names = [(board.board_id, board.board_name) for board in friend_boards]

    friend_dict = {}

    for item in friend_board_names:
        board_id = item[0]
        friend_dict[item] = []
        ratings = Rating.query.filter_by(board_id=board_id)
        for rating in ratings:
            md_image = rating.book.md_image
            friend_dict[item].append(md_image)

    # NEED TO TAKE OUT FUNCTIONALITY FOR PEOPLE TO MARK FRIEND'S STUFF

    return render_template("friend_boards.html", existing_boards=friend_boards, friend_dict=friend_dict, friend_name=friend_name)


@app.route('/logout')
def logout_user():
    """Logout user"""

    del session['logged_in']
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
