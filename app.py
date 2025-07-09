from flask import Flask, render_template, jsonify
from flask import send_from_directory
import requests
import random
import string

app = Flask(__name__)

API_BASE = "https://api.mail.tm"

# Generate random string
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Register and login to Mail.tm
def create_temp_account():
    # Get valid domain from mail.tm
    domain_res = requests.get(f"{API_BASE}/domains")
    if domain_res.status_code != 200:
        print("❌ Failed to fetch domains:", domain_res.text)
        return None

    domains = domain_res.json()["hydra:member"]
    if not domains:
        print("❌ No domains found")
        return None

    domain = domains[0]["domain"]  # use the first valid domain
    username = generate_random_string()
    email = f"{username}@{domain}"
    password = generate_random_string(12)

    # Create account
    create_res = requests.post(f"{API_BASE}/accounts", json={
        "address": email,
        "password": password
    })

    if create_res.status_code != 201:
        print("❌ Account creation failed:", create_res.text)
        return None

    # Login to get token
    token_res = requests.post(f"{API_BASE}/token", json={
        "address": email,
        "password": password
    })

    if token_res.status_code == 200:
        token_data = token_res.json()
        return {
            "email": email,
            "token": token_data["token"],
            "id": token_data["id"]
        }
    else:
        print("❌ Login failed:", token_res.text)
        return None

# Get inbox
def get_messages(token):
    headers = {"Authorization": f"Bearer {token}"}
    msg_res = requests.get(f"{API_BASE}/messages", headers=headers)
    if msg_res.status_code == 200:
        return msg_res.json()["hydra:member"]
    else:
        return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_email")
def get_email():
    account = create_temp_account()
    if not account:
        return jsonify({"error": "Failed to create email"}), 500
    return jsonify(account)

@app.route("/inbox/<token>")
def inbox(token):
    msgs = get_messages(token)
    return jsonify(msgs)

@app.route('/ads.txt')
def ads_txt():
    return send_from_directory('.', 'ads.txt')


if __name__ == "__main__":
    app.run(debug=True)
