from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask_app.models.article import Article
from flask import flash, session
import re
DB = "my_world_wiki"
class Subwiki:
    def __init__( self , data ):
        self.id = data['id']
        self.user_id = data['user_id']
        self.title = data['title']
        self.description = data['description']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.articles = []

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM subwikis;"
        results = connectToMySQL(DB).query_db(query)
        subwikis = []
        for subwiki in results:
            subwikis.append( cls(subwiki) )
        return subwikis
    
    @classmethod
    def get_by_id(cls, data):
        query = "SELECT * FROM subwikis WHERE id = %(id)s"
        results = connectToMySQL(DB).query_db(query,data)
        if not results:
            return False
        return cls(results[0])
    
    @classmethod
    def get_with_articles(cls, data, filter_viewable = False):
        query = """SELECT * FROM subwikis
                    LEFT JOIN articles
                    ON subwikis.id = subwiki_id
                    WHERE subwikis.id = %(id)s;"""
        results = connectToMySQL(DB).query_db(query,data)
        if not results:
            return False
        subwiki = cls(results[0])
        for dict in results:
            data = {
                'id': dict['articles.id'],
                'user_id': dict['articles.user_id'],
                'subwiki_id': dict['subwiki_id'],
                'title': dict['articles.title'],
                'viewable': dict['viewable'],
                'content': dict['content'],
                'created_at': dict['articles.created_at'],
                'updated_at': dict['articles.updated_at'],
            }
            if dict['articles.id']:
                if not (filter_viewable and data['viewable'] == 'friends'):
                    new_article = Article(data)
                    subwiki.articles.append(new_article)
        return subwiki
    
    @classmethod
    def save(cls, data):
        query = """INSERT INTO subwikis (user_id,title,description)
            VALUES (%(user_id)s,%(title)s,%(description)s);"""
        result = connectToMySQL(DB).query_db(query,data)
        return result
    
    @classmethod
    def update(cls,data):
        query = """UPDATE subwikis 
                SET title=%(title)s,description=%(description)s, updated_at=NOW() 
                WHERE id = %(id)s;"""
        return connectToMySQL(DB).query_db(query,data)
    
    @classmethod
    def delete(cls, data):
        subwiki = cls.get_with_articles(data)
        for article in subwiki.articles:
            article_data = {'id': article.id}
            result = Article.delete(article_data)
        query  = "DELETE FROM subwikis WHERE id = %(id)s;"
        return connectToMySQL(DB).query_db(query, data)
    
    @staticmethod
    def validate_subwiki(data):
        is_valid = True
        blank_field = False
        for key in data:
            if not data[key]:
                blank_field = True

        if blank_field:
            is_valid = False
            flash('Fields cannot be blank', 'subwiki')

        return is_valid
    
    @staticmethod
    def validate_action(id):
        is_valid = True
        object = Subwiki.get_by_id({'id': id})
        if object.user_id != session['user_id']:
            is_valid = False
        return is_valid