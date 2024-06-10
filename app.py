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
        
        session['user'] = request.form['name']

        return redirect(url_for('index'))
    
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
-Bobobo
-Bobobo

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

            return redirect(url_for('index'))
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

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    user = get_current_user()
    db = get_db()

    if request.method == 'POST':

        db.execute('INSERT into questions (question_text, asked_by_id, expert_id) values (?, ?, ?)',
                   [request.form['question'], user['id'], request.form['expert']])
        db.commit()

        return redirect(url_for('index'))

    experts_cur = db.execute('select id, name from users where expert = 1;')
    experts_result = experts_cur.fetchall()

    return render_template('ask.html', user=user, experts=experts_result)

@app.route('/unanswered')
def unanswered():
    user = get_current_user()

    db = get_db()
    questions_cur = db.execute("""select q.id, q.question_text, u.name \
                               from questions as q\
                               inner join users as u on q.asked_by_id = u.id\ 
                               where q.answer_text is null AND q.expert_id = ?""", [user['id']])
    questions_result = questions_cur.fetchall()

    return render_template('unanswered.html', user=user, questions=questions_result)

@app.route('/users')
def users():
    user = get_current_user()

    db = get_db()
    users_cur = db.execute('select id, name, expert, admin from users;')
    users_results = users_cur.fetchall()

    return render_template('users.html', user=user, users=users_results)

@app.route('/promote/<user_id>')
def promote(user_id):

    db = get_db()
    promo_cur = db.execute("select id, name, expert from users where id = ?", [user_id])
    promo_result = promo_cur.fetchone()

    if promo_result['expert'] == 1:
        db.execute("UPDATE users set expert = 0 where id = ?", [user_id])
    else:
        db.execute("UPDATE users set expert = 1 where id = ?", [user_id])
    
    db.commit()

    return redirect(url_for('users'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)