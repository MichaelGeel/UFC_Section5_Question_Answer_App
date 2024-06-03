from flask import Flask, render_template, g, request, url_for, session, redirect
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Creating the secret key using 24 random characters.

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def get_current_user():
    user_result = None

    if 'user' in session:
        user = session['user']

        db = get_db()
        user_cursor = db.execute('select id, name, password, expert, admin from users where name = ?', [user])
        user_result = user_cursor.fetchone()
    
    return user_result

@app.route('/')
def index():
    # Checking to see if the user is in the session:
    user = get_current_user()
    #if "user" in session:
    #    user = session['user']
    
    return render_template('home.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()

    if request.method == "POST":
        db = get_db()
        hashed_password = generate_password_hash(request.form['password'], method="pbkdf2")

        db.execute('insert into users (name, password, expert, admin) VALUES (?, ?, ?, ?)',
                   [request.form['name'], hashed_password, 0, 0]
                   )
        db.commit()
        
        return "<h1>User Created</h1>"
    
    return render_template('register.html', user=user)

"""
Users in the database:

####Admin:
-Mikey
-adpword

####Expert:
-Expy
-expword

####Regular:
-Reggie
-rgpword 
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()

    if request.method == 'POST':
        db = get_db()

        name = request.form['name']
        password = request.form["password"]

        user_cursor = db.execute('select id, name, password from users where name = ?', [name])
        user_result = user_cursor.fetchone()

        # Checking to see if the user entered password matches the password saved in the database.
        if check_password_hash(user_result['password'], password):

            session['user'] = user_result['name']

            return "<h1>The password is correct</h1>"
        else:
            return "<h1>The password is incorrect</h1>"


    return render_template('login.html', user=user)

@app.route('/question')
def question():
    user = get_current_user()

    return render_template('question.html', user=user)

@app.route('/answer')
def answer():
    user = get_current_user()

    return render_template('answer.html', user=user)

@app.route('/ask')
def ask():
    user = get_current_user()

    return render_template('ask.html', user=user)

@app.route('/unanswered')
def unanswered():
    user = get_current_user()

    return render_template('unanswered.html', user=user)

@app.route('/users')
def users():
    user = get_current_user()

    return render_template('users.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)