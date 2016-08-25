
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_triangle import Triangle
from models import *
from model import *
from search import *
from boards import add_board, add_new_book, add_rating, evaluate_ratings, get_bd_imgs, filter_by_read
from tsundoku import *
from login import process_new_login, process_new_registration
from friends import return_potential_friends, make_friend_dict
import datetime

app = Flask(__name__, static_path='/static')
Triangle(app)

app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined

#LOGIN AND REGISTRATION FUNCTIONS

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
    user_exists = User.get_user_by_username(username)

    #processes login with user object and entered password (see login.py)
    return process_new_login(user_exists, password)


@app.route('/register')
def register_user():
    """Process registration information"""

    return render_template('register.html')


@app.route('/process_registration', methods=['POST'])
def process_registration():
    """Processes user registration with form inputs"""

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    #queries the database for user based on username
    user_exists = User.get_user_by_username(username)

    #processes registration with user object, and entered info (see login.py)
    return process_new_registration(user_exists, username, email, password)


@app.route('/logout')
def logout_user():
    """Logout user"""

    del session['logged_in']
    flash("You are successfully logged out!")

    return redirect('/')


# SEARCH API AND PIN BOOK ROUTES


@app.route('/search')
def search():
    """Search API with search term given by user"""

    search_term = request.args.get('search')
    current_url = request.url

    #gets and processes search results from Amazon API (see search.py), by default gets first page
    results_list = process_result(search_API(search_term, 1))

    if not results_list:
        flash("Didn't find anything with that title! Please try again.")
        return redirect(request.referrer)

    #using session key, gets the boards for the logged-in user
    user_id = session['logged_in']
    existing_boards = Board.get_board_by_userid(user_id)

    #renders search template with the results list from API call. Allows user to click a modal window and add a book to a board.
    return render_template('search_results.html', results_list=results_list, existing_boards=existing_boards)


@app.route('/add_book', methods=['POST'])
def add_book():
    """Add book to board from search page"""

    #hidden form inputs
    title = request.form.get('title')
    author = request.form.get('author')
    asin = request.form.get('asin')
    md_image = request.form.get('md_image')
    lg_image = request.form.get('lg_image')
    url = request.form.get('url')
    num_pages = request.form.get('num_pages')
    primary_node_id = request.form.get('primary_node_id')
    primary_node = request.form.get('primary_node')
    parent_node_id = request.form.get('parent_node_id')
    parent_node = request.form.get('parent_node')
    #user form inputs
    board = request.form.get('board')
    hasread = request.form.get('hasread')
    rating = request.form.get('rating')
    notes = request.form.get('notes')

    #gets user id from session key
    user_id = session['logged_in']
    #gets current date and formats it in a string
    current_date = datetime.datetime.now().strftime('%m-%d-%y')

    primary_node_exists = check_for_node(primary_node_id, primary_node)
    parent_node_exists = check_for_node(parent_node_id, parent_node)

    #queries the database for book based on asin
    book_exists = Book.get_book_by_asin(asin)

    #if the book isn't in the database, adds both book and rating to the database
    #otherwise, uses the book id for the book currently in the db and creates a new rating
    if book_exists == None:
        new_book = add_new_book(asin, title, author, md_image, lg_image, url, num_pages, primary_node_id, parent_node_id)
        new_book_id = Book.get_book_by_asin(asin)
        new_rating = add_rating(new_book_id, user_id, board, current_date, hasread, rating, notes)
    else:
        current_book_id = book_exists
        new_rating = add_rating(current_book_id, user_id, board, current_date, hasread, rating, notes)

    flash('Book successfully added!')

    #redirects to the board details page (should now show recently added book)
    return redirect('/board_details/' + board)


# ROUTES TO CREATE AND VIEW USER BOARDS


@app.route('/create_board')
def create_board():
    """Allows user to create a board"""

    user_id = session['logged_in']

    #gets board ids by user and then makes a list of existing boards
    existing_boards = Board.get_board_by_userid(user_id)
    existing_board_ids_names = [(board.board_id, board.board_name) for board in existing_boards]

    #makes a dictionary of images associated w/user board for user in jinja template
    bd_img_dict = get_bd_imgs(existing_board_ids_names)

    # simple form input allowing user to specify a new board name
    return render_template("create_board.html", existing_boards=existing_boards, my_dict=bd_img_dict)


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
    user_id = session['logged_in']

    my_boards = [board.board_id for board in Board.get_board_by_userid(user_id)]

    if int(board_id) not in my_boards:
        flash("Oops, looks like you don't have a board with that ID.")

    session['board_id'] = board_id
    #gets ratings for that board, as well as board name
    ratings = get_ratings_by_board_id(board_id)
    board = Board.query.get(board_id).board_name

    #goes through the list of ratings and unpacks them into variables (see boards.py)
    books = evaluate_ratings(ratings)

    #get current friend info
    current_friends = get_current_friends(user_id)

    #get current recommendations
    my_recs = get_current_recs(user_id)

    #renders template showing books currently on the board
    return render_template("board_details.html", books=books, board_title=board, board_id=board_id, current_friends=current_friends, my_recs=my_recs)


# FUNCTIONALITY TO UPDATE RATING INFORMATION (NOTES, READ STATUS, SCORE)


@app.route('/get_notes')
def get_notes_for_rating():
    """Gets notes for a particular rating and passes back to JS callback"""

    rating_id = request.args.get('rating_id')

    notes = db.session.query(Rating.notes).filter(Rating.rating_id == rating_id).first()

    results = {'notes': notes}

    return jsonify(results)


@app.route('/update_notes', methods=['POST'])
def update_notes():
    """Updates notes for a particular rating"""

    rating_id = request.form.get('rating_id')
    notes = request.form.get('notes')
    rating = Rating.query.get(rating_id)
    board_id = rating.update_notes(notes)

    return redirect("/board_details/" + str(board_id))


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
    read_books = filter_by_read(hasread, user_id, board_id)

    #goes through the list of ratings and unpacks them into variables (see boards.py)
    books = evaluate_ratings(read_books)

    #get current friends
    current = Relationship.query.filter_by(primary_friend=user_id, status="Accepted").all()

    #get current friend info
    current_friends = [(friend.get_secondary_friend_info().user_name, friend.secondary_friend) for friend in current]

    #renders board details template again with filtered books
    return render_template("board_details.html", books=books, board_title=board, current_friends=current_friends)


@app.route('/read_book', methods=['POST'])
def mark_book_as_read():

    user_id = session['logged_in']

    #gets book id from JS post request
    book_id = request.form.get('book_id')

    #sets a message based on calling the "mark read" function that marks book read in the DB (see boards.py)
    this_rating = Rating.query.filter_by(user_id=user_id, book_id=book_id).first()
    message = this_rating.mark_read()

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
    this_rating = Rating.query.filter_by(user_id=user_id, book_id=book_id).first()
    asin = this_rating.update_rating(score)

    #returns asin and score in a dictionary to pass back to JS
    results = {'asin': asin, 'score': score}

    #returns jsonified dictionary of results dict
    return jsonify(results)


# RELATIONSHIP FUNCTIONALITY


@app.route('/find_friends')
def friend_search():
    """Renders page with search box for friends, pending relationships and current friends"""

    #gets user id from session, and searches database for any current pending relationships to display
    #NOTE - where user is requester.
    user_id = session['logged_in']

    pending_relationships = Relationship.query.filter_by(primary_friend=user_id, status="Pending", requesting_friend=True).all()

    #gets secondary friend info for each relationship in pending relationships
    secondary_friends = [(relationship.get_secondary_friend_info().user_name, relationship.relationship_id, relationship.status) for relationship in pending_relationships]

    #gets any requests that the user has received from others
    my_pending_requests = Relationship.query.filter_by(secondary_friend=user_id, status="Pending", requesting_friend=True).all()

    #gets requester info for pending requests
    requester_info = [(relationship.users.user_name, relationship.primary_friend, relationship.status) for relationship in my_pending_requests]

    #get current friends
    current = Relationship.query.filter_by(primary_friend=user_id, status="Accepted").all()

    #get current friend info
    current_friends = [(friend.get_secondary_friend_info().user_name, friend.secondary_friend) for friend in current]

    #renders search page along with any pending relationships, as defined above.
    return render_template('find_friends.html', pending_relationships=secondary_friends, pending_requests=requester_info, current_friends=current_friends)


@app.route('/search_friends')
def search_friends():
    """Processes search input from user and returns possible friends for selection"""

    #gets search term from search form, and user id from session
    friend = request.args.get('search')
    user_id = session['logged_in']

    #gets a dictionary of potential friend info from two functions in friends file
    possible_friends = make_friend_dict(return_potential_friends(user_id, friend))

    return render_template('possible_friends.html', friends=possible_friends)


@app.route('/add_friend/<friend_id>', methods=['POST', 'GET'])
def add_friend(friend_id):
    """Creates relationship between two users, with status 'Pending'"""

    user_id = session['logged_in']
    friend_user_id = friend_id

    added_message = add_relationships(user_id, friend_user_id)

    flash(added_message)

    return redirect("/find_friends")


@app.route('/accept_friend/<friend_id>', methods=['POST', 'GET'])
def accept_friend(friend_id):
    """Changes status of relationship(s) btwn two users to 'Accepted'"""

    user_id = session['logged_in']

    this_relationship_1 = Relationship.query.filter_by(primary_friend=user_id, secondary_friend=friend_id).first()
    this_relationship_2 = Relationship.query.filter_by(primary_friend=friend_id, secondary_friend=user_id).first()
    this_relationship_1.accept()
    accept_message = this_relationship_2.accept()

    flash(accept_message)

    return redirect('/find_friends')


@app.route('/deny_friend/<friend_id>', methods=['POST', 'GET'])
def deny_friend(friend_id):
    """Changes status of relationship(s) btwn two users to 'Denied'"""

    user_id = session['logged_in']

    this_relationship_1 = Relationship.query.filter_by(primary_friend=user_id, secondary_friend=friend_id).first()
    this_relationship_2 = Relationship.query.filter_by(primary_friend=friend_id, secondary_friend=user_id).first()
    this_relationship_1.deny()
    deny_message = this_relationship_2.deny()

    flash(deny_message)

    return redirect('/find_friends')


@app.route('/friend_boards/<friend_id>', methods=['POST', 'GET'])
def show_friend_boards(friend_id):
    """Shows overview page of a particular friend's boards"""

    friend_boards = Board.get_board_by_userid(friend_id)
    friend_name = User.query.get(friend_id).user_name
    friend_board_names = [(board.board_id, board.board_name) for board in friend_boards]

    friend_dict = get_bd_imgs(friend_board_names)

    return render_template("friend_boards.html", existing_boards=friend_boards, friend_dict=friend_dict, friend_name=friend_name)


@app.route('/friend_board_details/<board_id>', methods=['POST', 'GET'])
def show_friend_board_details(board_id):
    """Shows details of a particular board for a friend"""

    user_id = session['logged_in']

    ratings = get_ratings_by_board_id(board_id)
    board = Board.query.get(board_id).board_name
    my_boards = Board.get_board_by_userid(user_id)
    my_book_ids = [book.book_id for book in db.session.query(Rating.book_id).filter(Rating.user_id==user_id).all()]
    #goes through the list of ratings and unpacks them into variables (see boards.py)
    books = evaluate_ratings(ratings)

    #renders template showing books currently on the board
    return render_template("friend_board_details.html", books=books, board_title=board, board_id=board_id, existing_boards=my_boards, my_book_ids=my_book_ids)


@app.route('/add_friend_book', methods=['POST'])
def add_friend_book():
    """Adds book from a friend's board to user's board."""

    user_id = session['logged_in']

    book_id = request.form.get('book_id')

    board_id = request.form.get('board')

    hasread = request.form.get('hasread')

    rating = request.form.get('rating')

    rec_id = request.form.get('rec_id')

    current_date = datetime.datetime.now().strftime('%m-%d-%y')

    new_rating = add_rating(book_id, user_id, board_id, current_date, hasread, rating)

    if rec_id is not None:
        this_rec = Recommendation.query.filter_by(recommendation_id=rec_id).first()
        this_rec.status = "Accepted"
        db.session.commit()

    return redirect('/board_details/' + board_id)


@app.route('/recommend_book', methods=['POST'])
def recommend_book():
    """Creates book recommendation for a friend"""

    user_id = session['logged_in']
    friend_id = request.form.get('friend')
    book_id = request.form.get('book_id')
    comment = request.form.get('comment')
    board_id = session['board_id']

    #NOTE - this returns the relationship ID where the referring user is the primary friend.
    relationship_id = return_relationship_id(user_id, friend_id)

    msg = add_recommendation(relationship_id, user_id, friend_id, book_id, comment)

    flash(msg)

    return redirect('/board_details/' + board_id)

@app.route('/recommendations')
def show_recommendations():
    """Shows any recommendations you have from friends with status 'Pending'"""

    user_id = session['logged_in']

    recs_for_me = Recommendation.query.filter_by(referred_user=user_id, status="Pending").all()

    my_boards = Board.get_board_by_userid(user_id)

    rec_dict = {}

    for rec in recs_for_me:
        rec_dict[rec.recommendation_id] = {'book_id': rec.book_id, 'referring_user_id': rec.referring_user,
                                           'referring_user': rec.users.user_name, 'title': rec.bookinfo.title,
                                           'author': rec.bookinfo.author, 'md_image': rec.bookinfo.md_image,
                                           'comment': rec.comments}

    return render_template('my_recommendations.html', rec_dict=rec_dict, rec_list=recs_for_me, my_boards=my_boards)


@app.route('/ignore_rec', methods=['POST'])
def ignore_rec():
    """Sets recommendation status to 'Ignored' for selected recommendation."""

    rec_id = request.form.get('rec_id')
    this_rec = Recommendation.query.get(rec_id)
    this_rec_id = this_rec.ignore_rec()

    results = {'rec_id': this_rec_id}

    return jsonify(results)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    # app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host='0.0.0.0', debug=False, port=5000)
