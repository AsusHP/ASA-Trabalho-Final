import os
from dotenv import load_dotenv
load_dotenv()

host = os.getenv('host')
dbname = os.getenv('dbname')
password = os.getenv('password')
port = os.getenv('port')
user = os.getenv('user')
host_mensagem = os.getenv('host_mensagem')