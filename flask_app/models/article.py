from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask_app.models.section import Section
from flask_app.models import user
from flask import flash, session
import re
DATE_REGEX = re.compile(r'^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$')
DB = "my_world_wiki"
class Article:
    def __init__( self , data ):
        self.id = data['id']
        self.user_id = data['user_id']
        self.subwiki_id = data['subwiki_id']
        self.title = data['title']
        self.viewable = data['viewable']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.sections = []

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM articles;"
        results = connectToMySQL(DB).query_db(query)
        articles = []
        for article in results:
            articles.append( cls(article) )
        return articles
    
    @classmethod
    def get_by_id(cls, data):
        query = "SELECT * FROM articles WHERE id = %(id)s"
        results = connectToMySQL(DB).query_db(query,data)
        if not results:
            return False
        return cls(results[0])
    
    @classmethod
    def get_with_sections(cls, data):
        query = """SELECT * FROM articles
                    LEFT JOIN sections
                    ON articles.id = article_id
                    WHERE articles.id = %(id)s;"""
        results = connectToMySQL(DB).query_db(query,data)
        if not results:
            return False
        article = cls(results[0])
        for dict in results:
            data = {
                'id': dict['sections.id'],
                'subwiki_id': dict['sections.subwiki_id'],
                'article_id': dict['article_id'],
                'article_user_id': dict['article_user_id'],
                'article_subwiki_id': dict['article_subwiki_id'],
                'header': dict['header'],
                'content': dict['sections.content'],
                'created_at': dict['sections.created_at'],
                'updated_at': dict['sections.updated_at'],
            }
            if dict['sections.id']:

                new_section = Section(data)
                article.sections.append(new_section)
        # article.sections.reverse()
        return article
    
    @classmethod
    def save(cls, data):
        query = """INSERT INTO articles (user_id,subwiki_id,title,viewable)
            VALUES (%(user_id)s,%(subwiki_id)s,%(title)s,%(viewable)s);"""
        result = connectToMySQL(DB).query_db(query,data)
        return result
    
    @classmethod
    def update(cls,data):
        query = """UPDATE articles 
                SET user_id=%(user_id)s,title=%(title)s,viewable=%(viewable)s,
                updated_at=NOW() 
                WHERE id = %(id)s;"""
        return connectToMySQL(DB).query_db(query,data)
    
    @classmethod
    def delete(cls, data):
        article = cls.get_with_sections(data)
        for section in article.sections:
            section_data = {'id': section.id}
            result = Section.delete(section_data)
        query  = "DELETE FROM articles WHERE id = %(id)s;"
        return connectToMySQL(DB).query_db(query, data)
    
    @staticmethod
    def validate_article(article):
        is_valid = True

        if not article['title']:
            is_valid = False
            flash('Title cannot be blank', 'article')

        if (article['viewable'] != 'anyone') and (article['viewable'] != 'friends'):
            is_valid = False

        return is_valid
    
    @staticmethod
    def validate_action(article):
        is_valid = True
        if article['user_id'] != session['user_id']:
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_view(article):
        is_valid = True
        article = Article.get_by_id(article)
        friend_data = {
            'user_id': session['user_id'],
            'user_friend_id': article.user_id
        }
        is_friend = user.User.check_friend(friend_data)

        if (not is_friend) and (article.viewable != 'anyone'):
            is_valid = False

        return is_valid