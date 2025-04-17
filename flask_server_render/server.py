from flask import Flask, jsonify, request
import os
import sqlite3

app = Flask(__name__)

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
        ipadress TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Fonctions
def add_users(uid, ipadress):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT uid, ipadress FROM connectedusers WHERE uid = ?", (uid,))
    contacts = cursor.fetchall()

    if contacts and contacts[0] == (uid, ipadress):
        conn.close()
        return "DOES EXIST"
    else:
        cursor.execute("INSERT INTO connectedusers (uid, ipadress) VALUES (?, ?)", (uid, ipadress))
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
    cursor.execute("UPDATE connectedusers SET ipadress = ? WHERE uid = ?", (ipadress1, uid1))
    conn.commit()
    conn.close()

def listeofconnectedusers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT uid FROM connectedusers")
    contacts = cursor.fetchall()
    conn.close()
    return contacts

# Routes
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
    return f"{listeofconnectedusers()}"

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
