from flask import Flask, jsonify, request
import os
import sqlite3
import time
from threading import Thread, Lock

app = Flask(__name__)

db_lock = Lock()

# Connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect("connectedusers.db", check_same_thread=False)
    return conn

# Initialisation de la base
def init_db():
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            ipadress TEXT NOT NULL,
            last_seen INTEGER NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username1 TEXT NOT NULL,
            username2 TEXT NOT NULL,
            statut INTEGER NOT NULL
        )
        """)
        conn.commit()
        conn.close()

init_db()

# Ajouter un utilisateur
def add_users(username, password, ipadress):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return "DOES EXIST"
        else:
            last_seen = int(time.time())
            cursor.execute("INSERT INTO users (username, password, ipadress, last_seen) VALUES (?, ?, ?, ?)",
                           (username, password, ipadress, last_seen))
            conn.commit()
            conn.close()
            return "OK"

# Connexion utilisateur
def connect(username, password, ipadress):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({"error": "Authentification échouée"}), 401

        last_seen = int(time.time())
        cursor.execute("UPDATE users SET ipadress = ?, last_seen = ? WHERE username = ?", (ipadress, last_seen, username))
        conn.commit()
        conn.close()

        return jsonify({"status": "IP mise à jour"}), 200

# Envoyer une demande d'ami (et l'accepter automatiquement si croisée)
def send_friend_request(username, password, usernamefriend):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user or user[1] != password:
            conn.close()
            return "Identifiant ou mot de passe incorrect"

        cursor.execute("SELECT * FROM friends WHERE username1 = ? AND username2 = ?", (username, usernamefriend))
        relation1 = cursor.fetchone()

        cursor.execute("SELECT * FROM friends WHERE username1 = ? AND username2 = ?", (usernamefriend, username))
        relation2 = cursor.fetchone()

        if relation2 and relation2[3] == 0:
            cursor.execute("UPDATE friends SET statut = 1 WHERE username1 = ? AND username2 = ?",
                           (usernamefriend, username))
            conn.commit()
            conn.close()
            return "Demande acceptée automatiquement"

        elif relation1:
            conn.close()
            return "Demande déjà envoyée"

        else:
            cursor.execute("INSERT INTO friends (username1, username2, statut) VALUES (?, ?, ?)",
                           (username, usernamefriend, 0))
            conn.commit()
            conn.close()
            return "Demande envoyée"

# Lister les amis
def list_friends(username, password):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT username, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user or user[1] != password:
            conn.close()
            return {"error": "Identifiant ou mot de passe incorrect"}

        cursor.execute("""
            SELECT username2 FROM friends 
            WHERE username1 = ? AND statut = 1
            UNION
            SELECT username1 FROM friends 
            WHERE username2 = ? AND statut = 1
        """, (username, username))

        friends = [row[0] for row in cursor.fetchall()]
        conn.close()

        return {"friends": friends}

# Envoyer son Ip à chaque connexion
def send_ipadress(username, password, ipadress):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT username, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user or user[1] != password:
            conn.close()
            return {"error": "Identifiant ou mot de passe incorrect"}

        last_seen = int(time.time())
        cursor.execute("UPDATE users SET ipadress = ?, last_seen = ? WHERE username = ?",
                       (ipadress, last_seen, username))
        conn.commit()
        conn.close()
        return {"status": "IP mise à jour"}


# === ROUTES FLASK ===

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    ipadress = data.get("ipadress")
    result = add_users(username, password, ipadress)
    return jsonify({"status": result})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    ipadress = data.get("ipadress")
    return connect(username, password, ipadress)

@app.route('/friend-request', methods=['POST'])
def friend_request():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    usernamefriend = data.get("usernamefriend")
    result = send_friend_request(username, password, usernamefriend)
    return jsonify({"status": result})

@app.route('/friends', methods=['POST'])
def friends():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    result = list_friends(username, password)
    return jsonify(result)

@app.route('/get-friend-ip', methods=['POST'])
def get_friend_ip():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    friend_username = data.get('friend_username')

    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({"error": "Authentification échouée"}), 401

        cursor.execute("""
            SELECT * FROM friends 
            WHERE (username1 = ? AND username2 = ?) OR (username1 = ? AND username2 = ?)
        """, (username, friend_username, friend_username, username))
        are_friends = cursor.fetchone()
        if not are_friends:
            conn.close()
            return jsonify({"error": "Vous n'êtes pas amis"}), 403

        cursor.execute("SELECT ipadress FROM users WHERE username = ?", (friend_username,))
        friend = cursor.fetchone()
        conn.close()
        if friend:
            return jsonify({"ipadress": friend[0]})
        else:
            return jsonify({"error": "Utilisateur introuvable"}), 404


# Lancement de l'application
if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
