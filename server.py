
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Book, Rating, Board
import os
import lxml
from amazonproduct import API
import collections

access_key = os.environ['AWS_ACCESS_KEY_ID']
secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
associate_tag = os.environ['AWS_ASSOCIATE_TAG']

api = API(locale='us', access_key_id=access_key, secret_access_key=secret_key, associate_tag=associate_tag) #sets up api gateway w/keys above

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

#MY ROUTES GO HERE


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

        flash('Your account has been successfully created!')                #sets session key for logged in and redirects home (now should show search!)
        session['logged_in'] = username

        return redirect('/')


@app.route('/search')
def search():

    search_term = request.args.get('search')                    #gets search term from search box

    result = api.item_search('Books', Title=search_term, ResponseGroup='Images,ItemAttributes', paginate=False) #searches api with search term

    result_items = result.Items.Item                            #'Unpacks' data from result page into a list of items

    results_dict = collections.OrderedDict()                    #sets empty dictionary to hold result values

    for index in range(len(result_items)):                      #goes through every item in the list of result items by index value
        try:                                                    #sets attributes as below for each item (title, author, etc.)
            key = index + 1
            asin = result_items[index].ASIN
            title = result_items[index].ItemAttributes.Title
            author = result_items[index].ItemAttributes.Author
            md_image = result_items[index].MediumImage.URL
            lg_image = result_items[index].LargeImage.URL
        except AttributeError:
            title = ''
            author = ''
            md_image = ''
            lg_image = ''
        if len(title) > 0:                                      #if the result has a title, puts it into the results dictionary
            results_dict[key] = {'title': title, 'author': author, 'asin': asin, 'md_image': md_image, 'lg_image': lg_image}

    return render_template('search_results.html', results_dict=results_dict)

@app.route('/add_book', methods=['POST'])
def add_book():
    """Add book to board"""

    title = request.form.get('title')                           #gets book attributes (most using hidden inputs)
    author = request.form.get('author')
    asin = request.form.get('asin')
    md_image = request.form.get('md_image')
    lg_image = request.form.get('lg_image')

    return "I GOTCHU. Here's your stuff. {} {} {} {} {}".format(title, author, asin, md_image, lg_image) #returns page with form info (for now)


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
