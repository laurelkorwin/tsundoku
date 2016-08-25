"""LOGIN AND REGISTRATION FEATURES"""

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from model import *
import models


def process_new_login(user_object, password):
    """Given user object and a password, process user login."""

    if user_object != None and user_object.password == password:
        flash('Successfully logged in!')
        session['logged_in'] = user_object.user_id
        return redirect('/')
    elif user_object != None and user_object.password != password:
        flash('Incorrect password. Please reenter.')
        return redirect('/login')
    else:
        flash('User account not found. Please register.')
        return redirect('/register')


def process_new_registration(user_object, username, email, password):

    if user_object != None:
        flash('Oops, that user name is already registered. Please choose another.')
        return redirect('/register')
    else:
        new_user = User(user_name=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        new_user_id = User.get_user_by_username(username).user_id

        flash('Your account has been successfully created!')
        session['logged_in'] = new_user_id

        return redirect('/')
