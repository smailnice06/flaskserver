from flask import Flask, jsonify, request
import os
import sqlite3
import time
from threading import Thread

app = Flask(__name__)

# Fonction pour se connecter à la base de données
def get_db_connection():
    conn = sqlite3.connect("connectedusers.db", check_same_thread=False)
    return conn

# Initialisation de la base de données
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS connectedusers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER NOT NULL,
        ipadress TEXT NOT NULL,
        last_seen INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Fonctions principales
def add_users(uid, ipadress):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT uid, ipadress FROM connectedusers WHERE uid = ?", (uid,))
    contacts = cursor.fetchall()

    if contacts and contacts[0] == (uid, ipadress):
        conn.close()
        return "DOES EXIST"
    else:
        last_seen = int(time.time())
        cursor.execute("INSERT INTO connectedusers (uid, ipadress, last_seen) VALUES (?, ?, ?)", (uid, ipadress, last_seen))
        conn.commit()
        conn.close()

def getconnecters(uid1):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ipadress FROM connectedusers WHERE uid = ?", (uid1,))
    contacts = cursor.fetchall()
    conn.close()
    return contacts[0][0] if contacts else None

def updateconnectedusers(uid1, ipadress1):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE connectedusers SET ipadress = ?, last_seen = ? WHERE uid = ?", (ipadress1, int(time.time()), uid1))
    conn.commit()
    conn.close()

def listeofconnectedusers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT uid FROM connectedusers")
    contacts = cursor.fetchall()
    conn.close()
    return contacts

def clean_inactive_users(timeout=60):
    now = int(time.time())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM connectedusers WHERE ? - last_seen > ?", (now, timeout))
    conn.commit()
    conn.close()

# Routes Flask
@app.route('/')
def home():
    return "Bienvenue sur la page d'accueil!"

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        UID = data.get('value1')
        IPADRESS = data.get('value2')

        if not isinstance(UID, int) or not isinstance(IPADRESS, str):
            return jsonify({"error": "Les deux valeurs doivent être valides"}), 400

        add_users(UID, IPADRESS)
        return f"{getconnecters(UID)}"

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/register')
def register():
    users = listeofconnectedusers()
    # Convertir en format JSON : liste de dictionnaires
    return jsonify([{"uid": uid[0]} for uid in users])


@app.route('/isconnected', methods=['POST'])
def isconnected():
    try:
        data = request.json
        UID = data.get('value1')

        listofusers = listeofconnectedusers()

        for user in listofusers:
            if UID == user[0]:
                return "True"

        return "False"

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/getin', methods=['POST'])
def getin():
    try:
        data = request.json
        UID = data.get('value1')

        listofusers = listeofconnectedusers()

        for user in listofusers:
            if UID == user[0]:
                return f"{getconnecters(UID)}"

        return "False"

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        UID = data.get('value1')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM connectedusers WHERE uid = ?", (UID,))
        conn.commit()
        conn.close()

        return "TRUE"
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.json
        UID = data.get('value1')
        IPADRESS = data.get('value2')

        updateconnectedusers(UID, IPADRESS)
        return "OK"
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Fonction pour lancer le nettoyage dans un thread séparé
def clean_inactive_users_periodically():
    while True:
        clean_inactive_users()
        time.sleep(60)  # Nettoyage toutes les minutes

# Lancer le thread pour nettoyage des utilisateurs inactifs
if __name__ == '__main__':
    # Lancer un thread qui s'exécute en parallèle et nettoie toutes les minutes
    thread = Thread(target=clean_inactive_users_periodically)
    thread.daemon = True  # Terminer le thread lorsque le programme principal se termine
    thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
