from flask import Flask, jsonify, request
import os
import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect("connectedusers.db", check_same_thread=False)  # check_same_thread=False pour éviter les erreurs dans Flask
cursor = conn.cursor()

# Création de la table si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS connectedusers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL,
    ipadress TEXT NOT NULL
)
""")
conn.commit()

# Fonction pour ajouter un utilisateur
def add_users(uid, ipadress):
    cursor.execute("SELECT uid, ipadress FROM connectedusers WHERE uid = ?", (uid,))
    contacts = cursor.fetchall()
    
    if contacts and contacts[0] == (uid, ipadress):
        return "DOES EXIST"
    else:
        cursor.execute("INSERT INTO connectedusers (uid, ipadress) VALUES (?, ?)", (uid, ipadress))
        conn.commit()

# Fonction pour obtenir l'IP d'un utilisateur connecté
def getconnecters(uid1):
    cursor.execute("SELECT ipadress FROM connectedusers WHERE uid = ?", (uid1,))
    contacts = cursor.fetchall()
    if contacts:
        return contacts[0][0]
    return None

# Fonction pour mettre à jour l'adresse IP d'un utilisateur
def updateconnectedusers(uid1, ipadress1):
    cursor.execute("UPDATE connectedusers SET ipadress = ? WHERE uid = ?", (ipadress1, uid1))
    conn.commit()

# Fonction pour lister les utilisateurs connectés
def listeofconnectedusers():
    cursor.execute("SELECT uid FROM connectedusers")
    contacts = cursor.fetchall()
    return contacts

# Création de l'application Flask
app = Flask(__name__)

# Route d'accueil
@app.route('/')
def home():
    return "Bienvenue sur la page d'accueil!"

# Route pour soumettre les données (UID et IP)
@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Récupérer les données JSON de la requête
        data = request.json

        # Extraire les valeurs
        UID = data.get('value1')
        IPADRESS = data.get('value2')

        # Vérifier que les valeurs sont valides
        if not isinstance(UID, int) or not isinstance(IPADRESS, str):
            return jsonify({"error": "Les valeurs doivent être valides (UID doit être un entier et IP doit être une chaîne)"}), 400

        # Ajouter l'utilisateur
        result = add_users(UID, IPADRESS)

        return jsonify({"message": "Utilisateur ajouté ou déjà existant", "result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route pour obtenir la liste des utilisateurs connectés
@app.route('/register')
def register():
    return jsonify(listeofconnectedusers())

# Route pour vérifier si un utilisateur est connecté
@app.route('/isconnected', methods=['POST'])
def isconnected():
    try:
        data = request.json
        UID = data.get('value1')

        listofusers = listeofconnectedusers()

        for user in listofusers:
            if UID == user[0]:
                return jsonify({"connected": True})

        return jsonify({"connected": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route pour obtenir l'IP d'un utilisateur si connecté
@app.route('/getin', methods=['POST'])
def getin():
    try:
        data = request.json
        UID = data.get('value1')

        listofusers = listeofconnectedusers()

        for user in listofusers:
            if UID == user[0]:
                ip = getconnecters(UID)
                return jsonify({"ip": ip if ip else "Non disponible"})

        return jsonify({"message": "Utilisateur non trouvé"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route pour supprimer un utilisateur
@app.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        UID = data.get('value1')

        # Supprimer l'utilisateur de la base de données
        cursor.execute("DELETE FROM connectedusers WHERE uid = ?", (UID,))
        conn.commit()
        
        return jsonify({"message": "Utilisateur supprimé"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400    

# Route pour mettre à jour l'IP d'un utilisateur
@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.json
        UID = data.get('value1')
        IPADRESS = data.get('value2')

        updateconnectedusers(UID, IPADRESS)
        return jsonify({"message": "IP mise à jour avec succès"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Lancement de l'application
if __name__ == '__main__':
     port = int(os.environ.get("PORT", 5000))
     app.run(host="0.0.0.0", port=port)


