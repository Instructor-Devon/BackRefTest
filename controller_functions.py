from flask import render_template, redirect, request, flash, session
from models import User, Post
from config import bcrypt, db, app, stripe_keys
from werkzeug.utils import secure_filename
import stripe
import os

import re
# from app import User
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


def index():
    return render_template("index.html", users=User.query.all())

def register():
    errors = []

    if len(request.form['first_name']) < 2:
        errors.append("First name must be at least 2 characters")
        valid = False

    if len(request.form['last_name']) < 2:
        errors.append("Last name must be at least 2 characters")
        valid = False

    if not EMAIL_REGEX.match(request.form['email']):
        errors.append("Email must be valid")
        valid = False

    if len(request.form['password']) < 8:
        errors.append("Password must be at least 8 characters")
        valid = False

    #TODO: Validate email is unique
    user_check = User.query.filter_by(email=request.form["email"]).first()
    if user_check is not None:
        errors.append("Email is in use")
    
    if request.form['password'] != request.form['confirm']:
        errors.append("Passwords must match")
        valid = False

    if errors:
        for e in errors:
            flash(e)
    else:
        hashed = bcrypt.generate_password_hash(request.form["password"])
        new_user = None
        #TODO: Create New User
        file = request.files['pic']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        new_user = User(
            first_name = request.form["first_name"],
            last_name = request.form["last_name"],
            pic = filepath,
            email = request.form["email"],
            password = hashed
        )
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.id
        return redirect("/dashboard")

    return redirect("/")

def login():
    errors = []

    user_attempt = User.query.filter_by(email=request.form["email"]).first()
    #TODO: Query for user wiith provided email
    
    if not user_attempt:
        flash("Email/Password Incorrect")
        return redirect("/")

    if not bcrypt.check_password_hash(user_attempt.password, request.form["password"]):
        flash("Email/Password Incorrect")
        return redirect("/")

    session["user_id"] = user_attempt.id
    return redirect("/dashboard")

def logout():
    session.clear()
    return redirect("/")

    # get user from session
    if not "user_id" in session:
        return redirect("/")


def delete_account(user_id):

    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/logout")


def dashboard():
    
    logged_in = User.query.get(session["user_id"])
    #TODO: Query for user with session id

    all_posts = Post.query.all()
    #TODO: Query for all posts, ordered by the most recent


    return render_template("dashboard.html", user=logged_in, posts=all_posts)

def new_post():
    if not "user_id" in session:
        return redirect("/")
    

    new_post = Post(content=request.form["content"], author_id=session["user_id"])
    db.session.add(new_post)
    db.session.commit()

    return redirect("/dashboard")

def show_post(post_id):

    # query for a post with id
    post = Post.query.get(post_id)
    return render_template("post_details.html", post=post)

def update_post(post_id):

    # query for a post with id
    post = Post.query.get(post_id)

    # update with new stuff!
    post.content = request.form["content"]

    db.session.commit()

    return redirect("/dashboard")

def delete_post(post_id):

    # query for a post with id
    post = Post.query.get(post_id)

    # delete from db.session
    db.session.delete(post)

    # commit to db
    db.session.commit()

    return redirect("/dashboard")

def add_like(post_id):
    # query for a user (that's doing the liking)
    logged_in_user_id = session["user_id"]
    user = User.query.get(logged_in_user_id)

    # query for a post!
    post = Post.query.get(post_id)

    user.likes_sent.append(post)
    db.session.commit()

    return redirect("/dashboard")