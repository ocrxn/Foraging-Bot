import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('my_token')
GUILD = os.getenv('my_guild')
DB_URL = os.getenv('DATABASE_URL')
TRUNCATE = os.getenv('truncate_token')
