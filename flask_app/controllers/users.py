from flask_app import app
from flask import render_template,redirect,request, session
from flask_app.models.user import User
from flask_app.models.article import Article
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    session['subwiki_id'] = None
    if check_session():
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/register_user', methods = ['POST'])
def register_user():
    data = {
        'username': request.form['username'],
        'email': request.form['email'],
        'password': request.form['password'],
        'confirm_password': request.form['confirm-password'],
    }
    if not User.validate_user(data):
        return redirect('/')

    data['password'] = bcrypt.generate_password_hash(request.form['password'])
    del data['confirm_password']
    result = User.save(data)
    set_session(result, data['username'], True)
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if check_session():
        data = {
            'id': session['user_id']
        }
        user = User.get_user_with_subwikis(data)
        return render_template('dashboard.html', user = user)
    return redirect('/')

@app.route('/view_wiki/<int:id>')
def view_wiki(id):
    if check_session():
        if id == session['user_id']:
            return redirect('dashboard')
        data = {
            'id': id
        }
        user = User.get_user_with_subwikis(data)
        if user:
            return render_template('dashboard.html', user = user)
        return redirect('/find_users')
    return redirect('/')

@app.route('/log_out')
def log_out():
    session.clear()
    return redirect('/')

@app.route('/login_user', methods = ['POST'])
def login_user():
    data = {
        'email': request.form['email'],
        'password': request.form['password'],
    }
    if not User.validate_login(data):
        return redirect('/')
    user = User.get_user_by_email({'email': data['email']})
    set_session(user.id, user.username, True)
    return redirect('/dashboard')

@app.route('/update_user', methods = ['POST'])
def update_user():
    if check_session():
        data = {
            'id': session['user_id'],
            'username': request.form['username'],
        }
        if User.validate_update(data):
            result = User.update(data)
        return redirect('/account')
    return redirect('/')

@app.route('/clear_session')
def clear_session():
    session.clear()
    return redirect('/')

@app.route('/find_users')
def find_users():
    if check_session():
        users = User.get_all()
        return render_template('find_users.html', users = users)
    return redirect('/')

@app.route('/account')
def account():
    if check_session():
        data = {
            'id': session['user_id']
        }
        user = User.get_user_with_friends(data)
        return render_template('account.html', user = user)
    return redirect('/')

@app.route('/delete_user', methods = ['POST'])
def delete_user():
    if check_session():
        pass
        data = {
            'id': request.form.get('id')
        }
        if not User.validate_action(data):
            return redirect('/account')
        result = User.delete(data)
        return redirect('/clear_session')
    return redirect('/')

@app.route('/add_friend/<int:id>', methods = ['POST'])
def add_friend(id):
    if check_session():
        data = {
            'user_id': session['user_id'],
            'user_friend_id': id,
        }
        if User.validate_friend(data):
            result = User.add_friend(data)
        return redirect('/find_users')
    return redirect('/')

@app.route('/remove_friend/<int:id>', methods = ['POST'])
def remove_friend(id):
    if check_session():
        data = {
            'user_id': session['user_id'],
            'user_friend_id': id,
        }
        if User.validate_delete_friend(data):
            result = User.delete_friend(data)
        return redirect('/account')
    return redirect('/')

def check_session():
    if 'logged_in' in session and 'user_id' in session and 'username' in session:
        return True
    return False

def set_session(id, username, logged_in):
    session['user_id'] = id
    session['username'] = username
    session['logged_in'] = logged_in