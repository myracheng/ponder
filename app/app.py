from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_bootstrap import Bootstrap
from src.auth import auth_user, register_user
from src.user import PonderUser
from src.db import update_nos, update_yes, get_next_suggestion, create_profile, get_groups

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
    try:
        groups = get_groups();
        groups = [', '.join(l) for l in groups]
    except IndexError:
        groups = ['Global Chat']
    return render_template('chatrooms.html', groups=groups)


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
        session['username'] = user.username
        session['firstname'] = user.firstname
        session['lastname'] = user.lastname
        session['logged_in'] = True
        session['room'] = 'Global Chat'
        return hello_world()
    else:
        flash('Wrong password!')
        return login_page()


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
        return register_page()
    else:
        flash('Username taken! Please choose another username')
        return register_page()


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return hello_world()


@app.route('/swipe_page')
def swipe_page():
    username = str(session.get('username'))
    return render_template('swipe.html', user=get_next_suggestion(username), message='')


@app.route('/swipe', methods=['POST'])
def swipe():
    username = str(session.get('username'))
    print(request.form['swipe_value'] == 'nah')
    if request.form['swipe_value'] == 'yay':
        message = "One step closer to more effective studying!"
        new_yes = get_next_suggestion(username).username
        update_yes(username, new_yes)  # do swipe right
    elif request.form['swipe_value'] == 'nah':
        message = "Not today, partner"
        new_no = get_next_suggestion(username).username
        update_nos(username, new_no)  # do swipe left
    else:
        message = "An error occurred."
    return render_template('swipe.html', user=get_next_suggestion(username), message=message)


@app.route('/profile_page')
def profile_page():
    return render_template('profile.html')


@app.route('/profile', methods=['POST'])
def profile():
    noises = {'silent': 0, 'ambient': 1, 'loud': 2}
    collabs = {'moral': 0, 'discussion': 1}
    learns = {'audio': 1, 'visual': 2, 'kinesthetic': 3}
    envs = {'library': 1, 'visual': 2, 'room': 3, 'common': 4}
    username = session.get('username')

    noise = noises[request.form['noise']]
    collab = collabs[request.form['collab']]
    learn_style = learns[request.form['learn_style']]
    classes = request.form['class']
    major = request.form['major']
    env = envs[request.form['env']]

    create_profile(username, noise, collab, learn_style, classes, major, env)
    flash('Profile updated.')
    return profile_page()


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
    emit('message', {'msg': session.get('firstname') + ': ' + message['msg']}, room=room)


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


@app.errorhandler(404)
def page_not_found(e):
    return hello_world()


@app.errorhandler(405)
def method_not_allowed(e):
    return hello_world()


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    app.debug = True
    bootstrap = Bootstrap(app)
    socketio.init_app(app)
    socketio.run(app, debug=True, host='127.0.0.1', port=8080)
