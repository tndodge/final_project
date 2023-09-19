from flask_app import app
from flask import render_template,redirect,request, session
from flask_app.controllers.users import check_session
from flask_app.models.article import Article
from flask_app.models.user import User

@app.route('/view_article/<int:article_id>')
def view_article(article_id):
    if check_session():
        data = {'id': article_id}
        article = Article.get_with_sections(data)
        if article and Article.validate_view(data):
            return render_template('article.html', article = article)
    return redirect('/')

@app.route('/new_article')
def new_article():
    if check_session():
        data = {
            'id': session['user_id']
        }
        user = User.get_user_with_subwikis(data)
        if len(user.subwikis) > 0:
            return render_template('new_article.html', user = user)
    return redirect('/')

@app.route('/process_article', methods = ['POST'])
def process_article():
    if check_session():
        data = {
            'user_id': session['user_id'],
            'subwiki_id': request.form.get('subwiki'),
            'title': request.form['title'],
            'viewable': request.form.get('viewable'),
        }
        if Article.validate_article(data):
            result = Article.save(data)
            return redirect(f'/view_article/{result}')
        return redirect('/new_article')
    return redirect('/')

@app.route('/edit_article/<int:article_id>')
def edit_article(article_id):
    if check_session():
        article_data = {'id': article_id}
        article = Article.get_with_sections(article_data)
        data = {
            'id': session['user_id']
        }
        user = User.get_user_with_subwikis(data)
        data = {'user_id': article.user_id}
        if article and Article.validate_action(data):
            session['article_id'] = article_id
            return render_template('edit_article.html', article = article, user = user)
    return redirect('/')

@app.route('/update_article', methods = ['POST'])
def update_article():
    if check_session():
        data = {
            'id': session['article_id'],
            'user_id': session['user_id'],
            'title': request.form['title'],
            'viewable': request.form.get('viewable'),
        }
        if Article.validate_article(data):
            result = Article.update(data)
            return redirect(f'/view_article/{data["id"]}')
        return redirect(f'/edit_article/{session["article_id"]}')
    return redirect('/')

@app.route('/delete_article/<int:id>', methods = ['POST'])
def delete_article(id):
    article_id = id
    if check_session():
        data = {'id': article_id}
        article = Article.get_by_id(data)
        if article:
            data = {'user_id': article.user_id}
            if Article.validate_action(data):
                subwiki_id = article.subwiki_id
                data = {'id': article_id}
                result = Article.delete(data)
                return redirect(f'/subwiki/{subwiki_id}')
    return redirect('/')