import time
import sys
from flask import Flask, request, jsonify, abort, render_template # pip install Flask

# Il faudra importer la BDD

# Proxy fix
from werkzeug.middleware.proxy_fix import ProxyFix

# Password hashing
import bcrypt # pip install bcrypt

import random

import requests # pip install requests

# --- CONFIG ---

PASSWORD_HASH_ROUNDS = 10 # Bcrypt work factor. Increasing by 1 will double the work / number of iterations. Iterations = 2^PASSWORD_HASH_ROUNDS | It is recommended to use at least 10

# --- CODE ---

app = Flask(__name__)

# Proxy fix (https://flask.palletsprojects.com/en/3.0.x/deploying/apache-httpd/ & https://flask.palletsprojects.com/en/3.0.x/deploying/proxy_fix/)
# A RETIRER SI PAS UTILISé EN PROXY APACHE
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

"""
Pour envoyer une requête au backend : 

FLASK_BASE_URL = "https://notresite.com/flask/"
data = {
    "username": "john",
    "password": "secret"
}

endpoint_name = "login"

response = requests.post(FLASK_BASE_URL + endpoint_name, json=data)

if response.status_code == 200:
    response_json = response.json() # dict ou list, selon ce que renvoie l'endpoint
    
    auth_token = response_json["auth_token"] # par exemple
"""

print("Connecting to database...")
db_connection = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_DATABASE)

db_connection.autocommit = True # Execute automatiquement les requêtes au lieu de devoir faire db_connection.commit()
db_cursor = db_connection.cursor()

# MariaDB
db_cursor.execute("""CREATE TABLE IF NOT EXISTS credentials(
                        user_id BIGINT UNSIGNED PRIMARY KEY,
                        username VARCHAR(40),
                        password_hash VARCHAR(72),
                        creation_timestamp BIGINT
                    );""")
db_cursor.execute("""CREATE TABLE IF NOT EXISTS auth_tokens(
                        auth_token VARCHAR(30) PRIMARY KEY,
                        user_id BIGINT UNSIGNED,
                        creation_timestamp BIGINT,
                        expiration_timestamp BIGINT
                    );""")

print("Database connection and setup established!")

def fix_db_connection():
    global db_connection
    global db_cursor

    if not db_connection.is_connected():
        db_connection = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_DATABASE)

        db_connection.autocommit = True # Execute automatiquement les requêtes au lieu de devoir faire db_connection.commit()
        db_cursor = db_connection.cursor()

try:
    @app.route("/login", methods=["POST"])
    def login():
        data = request.json
        
        username = data["username"] # Renvoie 400 Bad request si "username" n'existe pas
        password = data["password"]
        
        # Hash password
        password = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=PASSWORD_HASH_ROUNDS)
        hashed = bcrypt.hashpw(password, salt)


        # Get DB info
        fix_db_connection()
        db_connection.start_transaction()
        db_cursor.execute("SELECT user_id, password_hash FROM credentials WHERE username = %s;", (username,))
        row = db_cursor.fetchone()
        if not row:
            abort(403)

        user_id = row[0]
        pw_hash = row[1]
        
        password = password.encode('utf-8')
        pw_hash = pw_hash.encode('utf-8')
        if not bcrypt.checkpw(password, pw_hash):
            abort(403) # Forbidden

        auth_token = generate_auth_token(user_id)
        db_connection.commit()

        return jsonify({"user_id": user_id, "auth_token": auth_token}), 200

    @app.route("/testRestricted", methods=["POST"])
    def testRestricted():
        data = request.json
        
        auth_token = data["auth_token"]
        user_id = check_auth_token(auth_token)

        return jsonify({"message": "Bravo, vous êtes authentifié !"}), 200

except Exception:
    if db_connection.is_connected():
        db_connection.rollback() # Rollback par précaution, car une erreur dans une requête est survenue


# Functions

def generate_auth_token(user_id: int) -> str:
    # auth_token: exactly 30 random characters from "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789._!?"
    char_set = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789._!?"

    auth_token = ""
    for i in range(30):
        auth_token += char_set[random.randint(0, len(char_set) - 1)]

    db_cursor.execute("INSERT INTO auth_tokens(auth_token, user_id, creation_timestamp) VALUES(%s, %s, %s);", (auth_token, user_id, int(time.time())))
    return auth_token

def check_auth_token(auth_token: str) -> int:
    fix_db_connection()
    db_cursor.execute("SELECT user_id FROM auth_tokens WHERE auth_token = %s;", (auth_token,))

    row = db_cursor.fetchone()
    if not row:
        abort(403) # Forbidden

    user_id = row[0]

    return user_id
