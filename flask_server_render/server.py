from flask import Flask, jsonify, request
import os
import sqlite3

conn = sqlite3.connect("connectedusers.db")
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS connectedusers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL,
    ipadress TEXT NOT NULL
)
""")
conn.commit()


def add_users(uid, ipadress):
    cursor.execute("SELECT uid,ipadress FROM connectedusers WHERE uid = ?", (uid,))
    contacts = cursor.fetchall()
    
    if contacts and contacts[0] == (uid, ipadress):
        return "DOES EXIST"
    else: 
        cursor.execute("INSERT INTO connectedusers (uid, ipadress) VALUES (?, ?)", (uid, ipadress))
        conn.commit()


def getconnecters(uid1):
    cursor.execute("SELECT ipadress FROM connectedusers WHERE uid = ?", (uid1,))
    contacts = cursor.fetchall()
    return contacts[0][0]

def updateconnectedusers(uid1,ipadress1):
    cursor.execute("UPDATE connectedusers SET ipadress = ? WHERE uid = ?", (ipadress1,uid1))
    conn.commit()

def listeofconnectedusers():
    cursor.execute("SELECT uid FROM connectedusers")
    contacts = cursor.fetchall()
    return contacts

app = Flask(__name__)

# Route pour la page d'accueil
@app.route('/')
def home():
    return "Bienvenue sur la page d'accueil!"

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Récupérer les données JSON de la requête
        data = request.json

        # Extraire les valeurs
        UID = data.get('value1')
        IPADRESS = data.get('value2')

        # Vérifier que les valeurs sont des entiers
        if not isinstance(UID, int) or not isinstance(IPADRESS, str):
            return jsonify({"error": "Les deux valeurs doivent être des entiers"}), 400

        
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

        tlistofusers = len(listofusers)

        for i in tlistofusers:
            if UID == listofusers[i][0]:
                return f"True"
        
        return f"False"


        
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/getin', methods=['POST'])
def getin():
    try:
        data = request.json

        UID = data.get('value1')

        listofusers = listeofconnectedusers()

        tlistofusers = len(listofusers)

        for i in tlistofusers:
            if UID == listofusers[i][0]:
                return f"{getconnecters(UID)}"
        else:
            return f"False"      
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        UID = data.get('value1')
        IPADRESS = data.get('value2')

        if IPADRESS in connectedusers:
            del connectedusers[UID]
            return "TRUE"
        else:
            return "False"
    except Exception as e:
        return jsonify({"error": str(e)}), 400    

@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.json
        UID = data.get('value1')
        IPADRESS = data.get('value2')

        updateconnectedusers(UID,IPADRESS)
        return "OK"
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
     port = int(os.environ.get("PORT", 5000))
     app.run(host="0.0.0.0", port=port)
