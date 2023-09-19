from flask_app import app
from flask import render_template,redirect,request, session
from flask_app.controllers.users import check_session
from flask_app.models.section import Section
from flask_app.models.article import Article
from flask_app.models.user import User

@app.route('/process_section', methods = ['POST'])
def process_section():
    if check_session():
        article_data = {'id': session['article_id']}
        article = Article.get_by_id(article_data)
        data = {
            'subwiki_id': article.subwiki_id,
            'article_id': article.id,
            'article_user_id': article.user_id,
            'article_subwiki_id': article.subwiki_id,
            'header': request.form['header'],
            'content': request.form['content'],
        }
        result = Section.save(data)
        return redirect(f'/edit_article/{article.id}')
    return redirect('/')

@app.route('/update_section', methods = ['POST'])
def update_section():
    if check_session():
        article_data = {'id': session['article_id']}
        article = Article.get_by_id(article_data)
        section = Section.get_by_id({'id': request.form.get('id')})
        section_data = {
            'id': request.form.get('id'),
            'subwiki_id': article.subwiki_id,
            'article_id': article.id,
            'article_user_id': article.user_id,
            'article_subwiki_id': article.subwiki_id,
            'header': request.form['header'],
            'content': request.form['content'],
        }
        data = {'user_id': section.article_user_id}
        if section and Section.validate_action(data):
            result = Section.update(section_data)
        return redirect(f'/edit_article/{article.id}')
    return redirect('/')

@app.route('/delete_section', methods = ['POST'])
def delete_section():
    if check_session():
        section_id = request.form.get('id')
        data = {'id': section_id}
        section = Section.get_by_id(data)
        if section:
            data = {'user_id': section.article_user_id}
            if Section.validate_action(data):
                data = {'id': section.id}
                result = Section.delete(data)
        return redirect(f'/edit_article/{session["article_id"]}')
    return redirect('/')