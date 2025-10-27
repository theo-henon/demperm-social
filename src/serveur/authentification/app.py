from flask import Flask, request, jsonify, render_template
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

app = Flask(__name__)

# Mettre son ID Google qui accepte votre domaine
GOOGLE_CLIENT_ID = "487631491277-nbbt1qft0po6nfhrmirlbhtrt796iqt2.apps.googleusercontent.com"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    token = data.get('token')

    try:
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(), GOOGLE_CLIENT_ID)

        # Vérifie que le token est bien destiné à ton client
        if idinfo['aud'] != GOOGLE_CLIENT_ID:
            print("Erreur de token google")
            raise ValueError('Audience mismatch')

        return jsonify({
            "valid": True,
            "name": idinfo.get("name"),
            "email": idinfo.get("email")
        })

    except Exception as e:
        print("Erreur de vérification :", e)
        return jsonify({"valid": False})

# Ma clef Google accepte http://localhost:5000
# Si vous voulez votre domaine, créez votre clef sur https://console.cloud.google.com/apis/credentials
if __name__ == '__main__':
    # app.run(host='172.20.0.3', port=5000) # l'adresse du docker que Nginx va faire dans mon cas
    app.run(host='127.0.0.1', port=5000) # , debug=True, use_reloader=False)
