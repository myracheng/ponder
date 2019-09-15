from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_socketio import SocketIO, emit, join_room, leave_room
from src.auth import auth_user, register_user
from src.user import PonderUser

import os
import random

socketio = SocketIO()

app = Flask(__name__)


@app.route('/')
def hello_world():
    if not session.get('logged_in'):
        return render_template('landing.html')
    else:
        return render_template('home.html', firstname=session['firstname'], lastname=session['lastname'], username=session['username'])


@app.route('/chatrooms_page')
def chatrooms_page():
    return render_template('chatrooms.html')


@app.route('/chatrooms', methods=['POST'])
def chatrooms():
    room = request.form['chatroom']
    session['room'] = room
    return chat()


@app.route('/login_page')
def login_page():
    return render_template('login.html')


@app.route('/register_page')
def register_page():
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = auth_user(username, password)
    if user:
        flash('Logged in!')
        session['username'] = user.username
        session['firstname'] = user.firstname
        session['lastname'] = user.lastname
        session['logged_in'] = True
        session['room'] = 'tmp'
    else:
        flash('wrong password!')
    return hello_world()


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']

    user = register_user(username, password, firstname, lastname, email)

    if user:
        flash('Success! Account created.')
    else:
        flash('username taken! please choose another username')
    return hello_world()


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return hello_world()


@app.route('/swipe_page')
def swipe_page():
    return render_template('swipe.html', user=PonderUser('user', 'Example', f'User{random.randint(1, 999)}'), message='')


@app.route('/swipe', methods=['POST'])
def swipe():
    if request.form['swipe_value'] == '<3':
        message = 'YOU SWIPED RIGHT :D'
        pass  # do swipe right
    elif request.form['swipe_value'] == '</3':
        message = 'YOU SWIPED LEFT D:'
        pass  # do swipe left
    else:
        message = "rip"
        pass  # process error
    return render_template('swipe.html', user=PonderUser('user', 'Example', f'User{random.randint(1, 999)}'), message=message)


@app.route('/profile_page')
def profile_page():
    return render_template('profile.html')


@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('firstname') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': session.get('firstname') + ':' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('firstname') + ' has left the room.'}, room=room)


@app.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    # name = session.get('name', '')
    name = session['firstname']
    room = session.get('room', '')
    # room = session['room']
    # if name == '' or room == '':
    #     return redirect(url_for('.index'))
    return render_template('chat.html', name=name, room=room)


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    app.debug = True
    socketio.init_app(app)
    socketio.run(app, debug=True, host='127.0.0.1', port=8080)
