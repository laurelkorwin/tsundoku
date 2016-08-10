"""LOGIN AND REGISTRATION FEATURES"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from model import connect_to_db, db, User, Book, Rating, Board
from tsundoku import get_user_by_username

def process_new_login(user_object, password):
    """Given user object and a password, process user login."""

    if user_object != None and user_object.password == password:    #checks to see if user is in DB, and is password matches.
        flash('Successfully logged in!')                            #If not, redirects to login / register accordingly.
        session['logged_in'] = user_object.user_id
        return redirect('/')
    elif user_object != None and user_object.password != password:
        flash('Incorrect password. Please reenter.')
        return redirect('/login')
    else:
        flash('User account not found. Please register.')
        return redirect('/register')

def process_new_registration(user_object, username, email, password):

    if user_object != None:                                     #Validates to see if username is in database (in case someone tries to pick one already in use)
        flash('Oops, that user name is already registered. Please choose another.')
        return redirect('/register')
    else:
        new_user = User(user_name=username, email=email, password=password) #adds user to DB with form inputs
        db.session.add(new_user)
        db.session.commit()
        new_user_id = get_user_by_username(username).user_id

        flash('Your account has been successfully created!')                #sets session key for logged in and redirects home (now should show search!)
        session['logged_in'] = new_user_id

        return redirect('/')

