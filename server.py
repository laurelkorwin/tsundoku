
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Book, Rating, Board
import os
import lxml
from amazonproduct import API

access_key = os.environ['AWS_ACCESS_KEY_ID']
secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
associate_tag = os.environ['AWS_ASSOCIATE_TAG']

api = API(locale='us', access_key_id=access_key, secret_access_key=secret_key, associate_tag=associate_tag)

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

    user_exists = User.query.filter_by(user_name=username).first()

    if user_exists != None and user_exists.password == password:
        flash('Successfully logged in!')
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

    if user_exists != None:
        flash('Oops, that user name is already registered. Please choose another.')
        return redirect('/register')
    else:
        new_user = User(user_name=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been successfully created!')
        session['logged_in'] = username

        return redirect('/')

@app.route('/search')
def search():

    search_term = request.args.get('search')

    result = api.item_search('Books', Title=search_term, ResponseGroup='Images,ItemAttributes', paginate=False)

    result_items = result.Items.Item

    results_dict = {}

    for index in range(len(result_items) - 1):
        try:
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
        if len(title) > 0:
            results_dict[key] = {'title': title, 'author': author, 'asin': asin, 'md_image': md_image, 'lg_image': lg_image}

    return render_template('search_results.html', results_dict=results_dict)

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
