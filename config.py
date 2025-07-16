import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('host_token')
USER = os.getenv('user_token')
PASSWORD = os.getenv('password_token')
DATABASE = os.getenv('database_token')
PORT = os.getenv('db_port')
TOKEN = os.getenv('my_token')
GUILD = os.getenv('my_guild')
TRUNCATE = os.getenv('truncate_token')
