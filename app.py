from flask import Flask, render_template, g, request, url_for, session
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def index():
    
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        db = get_db()
        hashed_password = generate_password_hash(request.form['password'], method="pbkdf2")

        db.execute('insert into users (name, password, expert, admin) VALUES (?, ?, ?, ?)',
                   [request.form['name'], hashed_password, 0, 0]
                   )
        db.commit()
        
        return "<h1>User Created</h1>"
    
    return render_template('register.html')

"""
Users in the database:

####Admin:
-Mikey
-adpword
"""

@app.route('/login')
def login():
    
    return render_template('login.html')

@app.route('/question')
def question():
    
    return render_template('question.html')

@app.route('/answer')
def answer():
    
    return render_template('answer.html')

@app.route('/ask')
def ask():
    
    return render_template('ask.html')

@app.route('/unanswered')
def unanswered():
    
    return render_template('unanswered.html')

@app.route('/users')
def users():
    
    return render_template('users.html')

if __name__ == "__main__":
    app.run(debug=True)