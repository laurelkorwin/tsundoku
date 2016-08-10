
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Book, Rating, Board
from search import setup_API, search_API, process_result
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

    user_exists = User.query.filter_by(user_name=username).first()  #gets first result if username exists in DB, otherwise gets None.

    if user_exists != None and user_exists.password == password:    #checks to see if user is in DB, and is password matches.
        flash('Successfully logged in!')                            #If not, redirects to login / register accordingly.
        session['logged_in'] = user_exists.user_id
        return redirect('/')
    elif user_exists != None and user_exists.password != password:
        flash('Incorrect password. Please reenter.')
        return redirect('/login')
    else:
        flash('User account not found. Please register.')
        return redirect('/register')


@app.route('/register')
def register_user():
    """Process registration information"""

    return render_template('register.html')


@app.route('/process_registration', methods=['POST'])
def process_registration():

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    user_exists = User.query.filter_by(user_name=username).first()

    if user_exists != None:                                     #Validates to see if username is in database (in case someone tries to pick one already in use)
        flash('Oops, that user name is already registered. Please choose another.')
        return redirect('/register')
    else:
        new_user = User(user_name=username, email=email, password=password) #adds user to DB with form inputs
        db.session.add(new_user)
        db.session.commit()
        new_user_id = User.query.filter_by(user_name=username).first().user_id

        flash('Your account has been successfully created!')                #sets session key for logged in and redirects home (now should show search!)
        session['logged_in'] = new_user_id

        return redirect('/')


@app.route('/search')
def search():

    search_term = request.args.get('search')

    results_list = process_result(search_API(search_term))
    user_id = session['logged_in']
    existing_boards = Board.query.filter_by(user_id=user_id).all()

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
    user_id = session['logged_in']
    current_date = datetime.datetime.now().strftime('%m-%d-%y')


    book_exists = Book.query.filter_by(asin=asin).first()

    if book_exists == None:
        new_book = Book(asin=asin, title=title, author=author, md_image=md_image, url=url)
        db.session.add(new_book)
        db.session.commit()
        new_book_id = Book.query.filter_by(asin=asin).first().book_id
        new_rating = Rating(book_id=new_book_id, user_id=user_id, board_id=board, date_added=current_date)
        db.session.add(new_rating)
        db.session.commit()
    else:
        current_book_id = book_exists.book_id
        new_rating = Rating(book_id=current_book_id, user_id=user_id, board_id=board, date_added=current_date)
        db.session.add(new_rating)
        db.session.commit()

    flash('Book successfully added!')

    return redirect('/board_details/' + board)

@app.route('/create_board')
def create_board():
    """Allows user to create a board"""

    user_id = session['logged_in']
    existing_boards = Board.query.filter_by(user_id=user_id).all()

    return render_template("create_board.html", existing_boards=existing_boards)

@app.route('/process_board', methods=['POST'])
def process_new_board():
    """Adds new board to the database."""

    board_name = request.form.get('board_name')
    date_created = datetime.datetime.now().strftime('%m-%d-%y')
    user_id = session['logged_in']

    new_board = Board(board_name=board_name, user_id=user_id, date_created=date_created)

    db.session.add(new_board)
    db.session.commit()
    flash('Your board successfully created!')

    return redirect('/create_board')

@app.route('/board_details/<board_id>')
def show_board_details(board_id):
    """Show books in board"""

    ratings = Rating.query.filter_by(board_id=board_id).all()
    board = Board.query.get(board_id).board_name

    books = []

    for rating in ratings:
        title = rating.book.title
        author = rating.book.author
        md_image = rating.book.md_image
        books.append({'title': title, 'author': author, 'md_image': md_image})

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
