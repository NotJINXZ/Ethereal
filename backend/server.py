from flask import Flask, redirect, render_template, request, session, url_for, jsonify
import sys
import json
import requests
import discord

with open("config.json", "r") as r:
    config = json.load(r)

app = Flask(__name__, template_folder="html", static_folder="static")
app.secret_key = "placeholder"

DISCORD_API_URL = "https://discord.com/api"

def get_discord_user(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{DISCORD_API_URL}/users/@me", headers=headers)
    return response.json()


def get_discord_guilds(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get("https://discord.com/api/users/@me/guilds", headers=headers)


    return response.json()

@app.route("/")
def index():
    if 'access_token' not in session:
        url = "/login" + "?id={}".format(request.args.get("id"))
        return redirect(url)
    
    if session.get("guild_id"):
        gid = session["guild_id"]
        print(gid)
        session.pop("guild_id")
        return redirect("/?id=" + str(gid))
    
    user_info = get_discord_user(session['access_token'])
    user_id = user_info.get('id', None)
    
    return render_template('index.html', user_id=user_id)

@app.route("/callback")
def callback():
    code = request.args.get('code')

    token_url = "https://discord.com/api/oauth2/token"
    data = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config["redirect_uri"],
        "scope": "identify guilds",
    }

    response = requests.post(token_url, data=data)
    response_data = response.json()

    if 'access_token' in response_data:
        session['access_token'] = response_data['access_token']
        return redirect(url_for('index'))
    else:
        return "Failed to obtain access token."

@app.route('/login')
def login():
    authorize_url = "https://discord.com/api/oauth2/authorize"

    redirected_id = request.args.get('id')
    if redirected_id:
        session['guild_id'] = redirected_id

    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": "identify guilds",
    }

    login_url = f"{authorize_url}?{'&'.join(f'{key}={value}' for key, value in params.items())}"
    return redirect(login_url)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/whitelist', methods=['POST'])
def whitelist():
    try:
        server_id = request.form.get('server_id')
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not server_id or not recaptcha_response:
            raise ValueError('Invalid request data')

        recaptcha_data = {
            'secret': config["recaptcha_secret"],
            'response': recaptcha_response
        }

        recaptcha_result = requests.post('https://www.google.com/recaptcha/api/siteverify', data=recaptcha_data).json()

        if not recaptcha_result.get('success'):
            return jsonify({"message": "reCAPTCHA validation failed", 'error': True}), 400

        print(f"Received request for server ID: {server_id}")

        def find(guild_id, data):
            for guild in data:
                if guild["id"] == guild_id:
                    return guild["name"], guild["owner"]
                
        name, owner = find(server_id, get_discord_guilds(session["access_token"]))
        if name is None:
            return jsonify({'message': 'Server was not found, are you sure you are in it?', 'error': True}), 404
        if not owner:
            return jsonify({'message': 'You do not own that server.', 'error': True}), 401

        with open("..\\whitelisted.json", "r") as r:
            data = json.load(r)
        
        data[str(server_id)] = True
        
        with open("..\\whitelisted.json", "w") as w:
            json.dump(data, w)
        
        return jsonify({'message': 'Server whitelisted successfully.'}), 200

    except Exception as e:
        print(f"Error processing whitelist request: {str(e)}")

        return jsonify({'message': 'An error occurred while processing the request', 'error': True}), 500

if __name__ == "__main__":
    PORT = 1122
    HOST = "0.0.0.0"

    if "--production" in sys.argv:
        import waitress
        print("Running in production mode on port: {}.".format(PORT))
        waitress.serve(app, host=HOST, port=PORT)
    else:
        print("Running in debugging mode on port: {}.".format(PORT))
        app.run(host=HOST, port=PORT, debug=True)
