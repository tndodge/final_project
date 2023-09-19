from flask_app import app
from flask import render_template,redirect,request, session
from flask_app.controllers.users import check_session
from flask_app.models.article import Article
from flask_app.models.subwiki import Subwiki
from flask_app.models.user import User

@app.route('/subwiki/<int:id>')
def sub_wiki(id):
    if check_session():
        subwiki = Subwiki.get_by_id({'id': id})
        friend_data = {
            'user_id': session['user_id'],
            'user_friend_id': subwiki.user_id
        }
        do_filter = (not User.check_friend(friend_data))
        subwiki = Subwiki.get_with_articles({'id': id}, do_filter)
        if subwiki:
            session['subwiki_id'] = subwiki.id
            return render_template('subwiki.html', subwiki = subwiki)
    return redirect('/')

@app.route('/new_subwiki')
def new_subwiki():
    if check_session():
        return render_template('new_subwiki.html')
    return redirect('/')

@app.route('/process_subwiki', methods = ['POST'])
def process_subwiki():
    if check_session():
        data = {
            'user_id': session['user_id'],
            'title': request.form['title'],
            'description': request.form['description'],
        }
        if not Subwiki.validate_subwiki(data):
            return redirect('new_subwiki')
        result = Subwiki.save(data)
    return redirect('/')

@app.route('/edit_subwiki/<id>')
def edit_subwiki(id):
    if check_session():
        subwiki = Subwiki.get_by_id({'id': id})
        if subwiki and Subwiki.validate_action(id):
            session['subwiki_id'] = id
            return render_template('edit_subwiki.html', subwiki = subwiki)
    return redirect('/')

@app.route('/update_subwiki', methods = ['POST'])
def update_subwiki():
    if check_session():
        data = {
            'id': session['subwiki_id'],
            'title': request.form['title'],
            'description': request.form['description'],
        }
        if not Subwiki.validate_subwiki(data):
            return redirect(f'edit_subwiki/{data["id"]}')
        result = Subwiki.update(data)
    return redirect('/')

@app.route('/delete_subwiki/<int:id>', methods = ['POST'])
def delete_subwiki(id):
    if check_session():
        if Subwiki.validate_action(id):
            result = Subwiki.delete({'id': id})
    return redirect('/')