from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask import flash, session
import re
DATE_REGEX = re.compile(r'^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$')
DB = "my_world_wiki"
class Section:
    def __init__( self , data ):
        self.id = data['id']
        self.subwiki_id = data['subwiki_id']
        self.article_id = data['article_id']
        self.article_user_id = data['article_user_id']
        self.article_subwiki_id = data['article_subwiki_id']
        self.header = data['header']
        self.content = data['content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM sections;"
        results = connectToMySQL(DB).query_db(query)
        sections = []
        for section in results:
            sections.append( cls(section) )
        return sections
    
    @classmethod
    def get_by_id(cls, data):
        query = "SELECT * FROM sections WHERE id = %(id)s"
        results = connectToMySQL(DB).query_db(query,data)
        if not results:
            return False
        return cls(results[0])
    
    @classmethod
    def save(cls, data):
        query = """INSERT INTO sections (subwiki_id,article_id,article_user_id,article_subwiki_id,
                    header,content)
                VALUES (%(subwiki_id)s,%(article_id)s,%(article_user_id)s,%(article_subwiki_id)s,
                        %(header)s,%(content)s);"""
        result = connectToMySQL(DB).query_db(query,data)
        return result
    
    @classmethod
    def update(cls,data):
        query = """UPDATE sections 
                SET subwiki_id=%(subwiki_id)s,article_id=%(article_id)s,article_user_id=%(article_user_id)s,
                article_subwiki_id=%(article_subwiki_id)s,header=%(header)s,content=%(content)s,updated_at=NOW() 
                WHERE id = %(id)s;"""
        return connectToMySQL(DB).query_db(query,data)
    
    @classmethod
    def delete(cls, data):
        query  = "DELETE FROM sections WHERE id = %(id)s;"
        return connectToMySQL(DB).query_db(query, data)
    
    @staticmethod
    def validate_section(section):
        is_valid = True

        return is_valid
    
    @staticmethod
    def validate_action(section):
        is_valid = True
        if section['user_id'] != session['user_id']:
            is_valid = False
        return is_valid