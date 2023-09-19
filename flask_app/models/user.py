from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask_app.models.subwiki import Subwiki
from flask import flash, session
import re
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*\d)(?=.*[A-Z]).+$')
DB = "my_world_wiki"
class User:
    def __init__( self , data ):
        self.id = data['id']
        self.username = data['username']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.subwikis = []
        self.friends = []
        self.is_friend = False
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(DB).query_db(query)
        users = []
        for user in results:
            users.append( cls(user) )
        return users
    
    @classmethod
    def get_user_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL(DB).query_db(query,data)
        return cls(result[0])
    
    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        result = connectToMySQL(DB).query_db(query,data)
        return cls(result[0])
    
    @classmethod
    def get_user_with_subwikis(cls, data):
        query = """SELECT * FROM users
                LEFT JOIN subwikis
                ON users.id = user_id
                WHERE users.id = %(id)s;"""
        result = connectToMySQL(DB).query_db(query,data)
        if not result:
            return False
        user = cls(result[0])
        for subwiki_dict in result:
            data = {
                'id': subwiki_dict['subwikis.id'],
                'user_id': subwiki_dict['user_id'],
                'title': subwiki_dict['title'],
                'description': subwiki_dict['description'],
                'created_at': subwiki_dict['subwikis.created_at'],
                'updated_at': subwiki_dict['subwikis.updated_at'],
            }

            if subwiki_dict['title']:

                new_subwiki = Subwiki(data)
                user.subwikis.append(new_subwiki)
        return user
    
    @classmethod
    def get_user_with_friends(cls, data):
        query = """SELECT * FROM users
                LEFT JOIN friends ON friends.user_id = users.id OR friends.user_friend_id = users.id
                LEFT JOIN users AS user_friends ON 
                (friends.user_friend_id = user_friends.id OR 
                friends.user_id = user_friends.id) AND user_friends.id != users.id
                WHERE users.id = '%(id)s';"""
        results = connectToMySQL(DB).query_db(query,data)
        if not results:
            return False
        user = cls(results[0])
        for friend_data in results:
            data = {
                'id': friend_data['user_friends.id'],
                'username': friend_data['user_friends.username'],
                'email': friend_data['user_friends.email'],
                'password': friend_data['user_friends.password'],
                'created_at': friend_data['user_friends.created_at'],
                'updated_at': friend_data['user_friends.updated_at'],
            }
            if data['username']:
                friend = cls(data)
                user.friends.append(friend)
        return user
    
    @classmethod
    def save(cls, data):
        query = """INSERT INTO users (username,email,password)
            VALUES (%(username)s,%(email)s,%(password)s);"""
        result = connectToMySQL(DB).query_db(query,data)
        return result
    
    @classmethod
    def update(cls,data):
        query = """UPDATE users 
                SET username=%(username)s,updated_at=NOW() 
                WHERE id = %(id)s;"""
        return connectToMySQL(DB).query_db(query,data)
    
    @classmethod
    def delete(cls, data):
        cls.delete_all_friends(data)
        user = cls.get_user_with_subwikis(data)
        for subwiki in user.subwikis:
            subwiki_data = {'id': subwiki.id}
            result = Subwiki.delete(subwiki_data)
        query  = "DELETE FROM users WHERE id = %(id)s;"
        return connectToMySQL(DB).query_db(query, data)
    
    @classmethod
    def delete_all_friends(cls, data):
        query = """DELETE FROM friends
                WHERE user_id = %(id)s OR user_friend_id = %(id)s;"""
        return connectToMySQL(DB).query_db(query,data)
    
    @classmethod
    def add_friend(cls, data):
        query = """INSERT INTO friends (user_id, user_friend_id)
            VALUES (%(user_id)s,%(user_friend_id)s);"""
        result = connectToMySQL(DB).query_db(query,data)
        return result
    
    @classmethod
    def delete_friend(cls, data):
        query = """DELETE FROM friends
                WHERE (user_id = %(user_id)s AND user_friend_id = %(user_friend_id)s) OR
                (user_id = %(user_friend_id)s AND user_friend_id = %(user_id)s);"""
        result = connectToMySQL(DB).query_db(query,data)
        return result
    
    @staticmethod
    def check_friend(friend):

        is_friend = True

        if friend['user_id'] != friend['user_friend_id']:
            is_friend = (not User.validate_friend(friend))

        return is_friend
    
    @staticmethod
    def validate_user(user):
        is_valid = True
        invalid_email_password = False
        username_unique = True
        email_unique = True

        data = {'username': user['username']}
        query = 'SELECT * FROM users WHERE username=%(username)s;'
        result = connectToMySQL(DB).query_db(query, data)
        if result:
            username_unique = False

        data = {'email': user['email']}
        query = 'SELECT * FROM users WHERE email=%(email)s;'
        result = connectToMySQL(DB).query_db(query, data)
        if result:
            email_unique = False

        if not user['username']:
            flash('Username is required', 'register')
            is_valid = False
        else:
            if len(user['username']) < 3:
                flash('Username must be at least 3 characters', 'register')
                is_valid = False
            elif not username_unique:
                is_valid = False
                flash('That username is unavailable', 'register')
        if not user['email']:
            invalid_email_password = True
            is_valid = False
        else:
            if not EMAIL_REGEX.match(user['email']):
                invalid_email_password = True
                is_valid = False
            elif not email_unique:
                invalid_email_password = True
                is_valid = False
        if not user['password']:
            invalid_email_password = True
            is_valid = False
        else:
            if len(user['password']) < 8:
                invalid_email_password = True
                is_valid = False
            if not PASSWORD_REGEX.match(user['password']):
                invalid_email_password = True
                is_valid = False
            elif user['password'] != user['confirm_password']:
                flash('Passwords do not match', 'register')
                is_valid = False
        if invalid_email_password:
            flash('Invalid email or password', 'register')
        return is_valid
    
    @staticmethod
    def validate_login(login):
        is_valid = True
        query = "SELECT password FROM users WHERE email = %(email)s;"
        result = connectToMySQL(DB).query_db(query,login)
        if len(result) > 0:
            password = result[0]['password']
        else:
            password = None
        if not login['email']:
            flash('Email is required', 'login')
            is_valid = False
        if not login['password']:
            flash('Password is required', 'login')
            is_valid = False
        if login['email'] and login['password'] and password:
            if not (bcrypt.check_password_hash(password, login['password'])):
                flash('Invalid email or password', 'login')
                is_valid = False
        else:
            flash('Invalid email or password', 'login')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_update(user):
        is_valid = True
        username_unique = True

        data = {'username': user['username']}
        query = 'SELECT * FROM users WHERE username=%(username)s;'
        result = connectToMySQL(DB).query_db(query, data)
        if result:
            username_unique = False

        if not user['username']:
            flash('Username cannot be blank', 'update')
            is_valid = False
        else:
            if len(user['username']) < 3:
                flash('Username must be at least 3 characters', 'update')
                is_valid = False
            elif not username_unique:
                is_valid = False
                flash('That username is unavailable', 'update')

        return is_valid
    
    def validate_action(user_data):
        is_valid = True
        user_id = int(user_data['id'])
        if session['user_id'] != user_id:
            is_valid = False
        print (session['user_id'], user_data['id'])
        return is_valid
    
    def validate_friend(friend):
        is_valid = True

        query = """SELECT * FROM friends
                WHERE (user_id = %(user_id)s AND user_friend_id = %(user_friend_id)s) OR
                (user_id = %(user_friend_id)s AND user_friend_id = %(user_id)s);"""
        
        result = connectToMySQL(DB).query_db(query, friend)

        if result:
            is_valid = False

        return is_valid
    
    def validate_delete_friend(friend):
        is_valid = True

        return is_valid