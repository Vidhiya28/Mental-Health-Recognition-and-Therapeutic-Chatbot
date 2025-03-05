from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
from chatbot import get_chatbot_response
from user_data import get_user_data
from database import register_user, verify_user
import os
import time

app = Flask(__name__, template_folder="templates")  # Explicitly set template path
app.secret_key = "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"


FILE_PATH = "user_predictions/user_responses.csv"

# Cache responses to reduce file I/O
cached_responses = None
last_load_time = 0

def load_responses():
    global cached_responses, last_load_time
    if cached_responses is None or time.time() - last_load_time > 30:  # Reload every 30 sec
        if os.path.exists(FILE_PATH):
            cached_responses = pd.read_csv(FILE_PATH)
        else:
            cached_responses = pd.DataFrame()
        last_load_time = time.time()
    return cached_responses

# Route: Home (Redirects to login if not authenticated)
@app.route('/')
def home():
    if "email" in session:
        return redirect(url_for("chat"))
    return redirect(url_for("login"))

# Route: Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        if verify_user(email, password):
            session["email"] = email  # Store user in session
            return redirect(url_for("chat"))
        else:
            return render_template("login.html", error="Invalid credentials!")

    return render_template("login.html")

# Route: Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        if register_user(email, password):
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="Email already exists!")

    return render_template("register.html")

# Route: Chatbot Page
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if "email" not in session:
        return redirect(url_for("login"))

    df = load_responses()
    user_data = df[df["email"] == session["email"]]
    disorders = [col for col in user_data.columns[-8:] if user_data.iloc[0][col] == 1] if not user_data.empty else []

    return render_template("index.html", user_data={"disorders": disorders})

@app.route('/chat_api', methods=['POST'])
def chat_api():
    if "email" not in session:
        return jsonify({"response": "Please log in first!"})

    email = session["email"]
    user_message = request.form["message"]
    
    df = load_responses()
    user_data = df[df["email"] == email]

    if user_data.empty:
        user_disorders = []
    else:
        user_disorders = [col for col in user_data.columns[-8:] if user_data.iloc[0][col] == 1]

    chatbot_response = get_chatbot_response(email, user_message, user_disorders)

    return jsonify({"response": chatbot_response})

# Route: Logout
@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)
