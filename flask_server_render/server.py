from flask import Flask, jsonify, request
import os

connectedusers = {}

app = Flask(__name__)

@app.route('/')
def home():
    return "Bienvenue sur la page d'accueil!"

@app.route('/hello/<name>')
def hello_name(name):
    return f"Bonjour, {name}!"

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        UID = data.get('value1')
        IPADRESS = data.get('value2')
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
        return f"{UID in connectedusers}"
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/getin', methods=['POST'])
def getin():
    try:
        data = request.json
        UID = data.get('value1')
        return f"{connectedusers.get(UID, 'False')}"
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
