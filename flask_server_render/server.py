from flask import Flask, jsonify, request

connectedusers = {}

app = Flask(__name__)

# Route pour la page d'accueil
@app.route('/')
def home():
    return "Bienvenue sur la page d'accueil!"

# Route dynamique pour saluer un utilisateur
@app.route('/hello/<name>')
def hello_name(name):
    return f"Bonjour, {name}!"

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

        
        connectedusers[UID] = IPADRESS

        return f"{connectedusers[UID]}"

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/register')
def register():
    return f"{connectedusers}"

@app.route('/isconnected', methods=['POST'])
def isconnected():
    try:
        data = request.json

        UID = data.get('value1')

        if UID in connectedusers:
            return f"True"
        else:
            return f"False"
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/getin', methods=['POST'])
def getin():
    try:
        data = request.json

        UID = data.get('value1')

        if UID in connectedusers:
            return f"{connectedusers[UID]}"
        else:
            return f"False"      
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
