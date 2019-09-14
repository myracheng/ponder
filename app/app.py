from flask import Flask, flash, redirect, render_template, request, session, abort
from src import auth
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        print(session)
        return f'Hello, {session["firstname"]}! <a href="/logout">Logout</a>'


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = auth(username, password)
    if user:
        flash('Logged in!')
        session['username'] = user.username
        session['firstname'] =  user.firstname
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return hello_world()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return hello_world()


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='127.0.0.1', port=8080)
