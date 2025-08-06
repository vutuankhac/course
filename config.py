import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    # MYSQL_DB = 'personal_website'
    MYSQL_DB = 'test'

class Hieu:
    hobbies = ("an", "ngu", "nghi", "choi")