from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
import time
from keras.models import load_model

from database import register_user, verify_user
from user_predictions.model import predict_user_disorder
from chatbot import get_chatbot_response
from huggingface_api import query_model

# Directory for journal storage
JOURNAL_DIR = "user_predictions/journals"
os.makedirs(JOURNAL_DIR, exist_ok=True)

# Flask App Config
app = Flask(__name__, template_folder="templates")
app.secret_key = "your-super-secret-key"

# Paths
SAVE_FOLDER = "user_predictions"
USER_RESPONSES_PATH = os.path.join(SAVE_FOLDER, "user_responses.csv")
MODEL_PATH = load_model("mental_health_model.h5")

# Cached data
cached_responses = None
last_load_time = 0

def load_responses():
    global cached_responses, last_load_time
    if cached_responses is None or time.time() - last_load_time > 30:
        if os.path.exists(USER_RESPONSES_PATH):
            cached_responses = pd.read_csv(USER_RESPONSES_PATH)
        else:
            cached_responses = pd.DataFrame()
        last_load_time = time.time()
    return cached_responses

def save_responses(df):
    df.to_csv(USER_RESPONSES_PATH, index=False)

def binary_convert(value):
    return 1 if value.lower() == "yes" else 0

# Home Page
@app.route('/')
def home():
    return render_template("home.html")

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    alert = session.pop("alert", None)
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        if verify_user(email, password):
            session["email"] = email
            df = load_responses()
            if not df[df["email"] == email].empty:
                return redirect(url_for("chat"))
            else:
                return redirect(url_for("form"))
        else:
            error = "Invalid credentials!"

    return render_template("login.html", error=error, alert=alert)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        if register_user(email, password):
            session["alert"] = "Registered successfully! Please login."
            return redirect(url_for("login"))
        else:
            error = "Email already exists!"

    return render_template("register.html", error=error)

# Logout
@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))

# Form Page
@app.route('/form', methods=['GET', 'POST'])
def form():
    if "email" not in session:
        return redirect(url_for("login"))

    email = session["email"]
    df = load_responses()

    if request.method == "POST":
        new_response = {
            "email": email,
            "Gender": request.form.get("Gender"),
            "Age": request.form.get("Age", type=int),
            "Academic Pressure": request.form.get("Academic Pressure", type=int),
            "Work Pressure": request.form.get("Work Pressure", type=int),
            "Sleep Duration": request.form.get("Sleep Duration", type=float),
            "Have you ever had suicidal thoughts ?": binary_convert(request.form.get("Have you ever had suicidal thoughts ?", "No")),
            "Work/Study Hours": request.form.get("Work/Study Hours", type=float),
            "Financial Stress": request.form.get("Financial Stress", type=int),
            "Social Activity Level": request.form.get("Social Activity Level", type=int),
            "Physical Activity Level": request.form.get("Physical Activity Level", type=int),
            "Screen Time per Day (hrs)": request.form.get("Screen Time per Day (hrs)", type=float),
            "Mood Swings Frequency": request.form.get("Mood Swings Frequency", type=int),
            "Panic Attacks Experience": binary_convert(request.form.get("Panic Attacks Experience", "No")),
            "Concentration Level": request.form.get("Concentration Level", type=int),
            "Intrusive Thoughts": binary_convert(request.form.get("Intrusive Thoughts", "No")),
            "Traumatic Experience History": binary_convert(request.form.get("Traumatic Experience History", "No")),
        }

        if email in df["email"].values:
            df.loc[df["email"] == email, new_response.keys()] = new_response.values()
        else:
            df = pd.concat([df, pd.DataFrame([new_response])], ignore_index=True)

        save_responses(df)
        return redirect(url_for("predictions"))

    user_data = df[df["email"] == email].to_dict(orient="records")
    user_data = user_data[0] if user_data else {}

    return render_template("form.html", email=email, user_data=user_data)

# Submit Form (redundant if you're using /form POST)
@app.route('/submit', methods=['POST'])
def submit():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    email = session["email"]
    df = load_responses()

    new_response = {
        "email": email,
        "Gender": request.form.get("Gender"),
        "Age": request.form.get("Age", type=int),
        "Academic Pressure": request.form.get("Academic Pressure", type=int),
        "Work Pressure": request.form.get("Work Pressure", type=int),
        "Sleep Duration": request.form.get("Sleep Duration", type=float),
        "Have you ever had suicidal thoughts ?": request.form.get("Have you ever had suicidal thoughts ?", "No"),
        "Work/Study Hours": request.form.get("Work/Study Hours", type=float),
        "Financial Stress": request.form.get("Financial Stress", type=int),
        "Social Activity Level": request.form.get("Social Activity Level", type=int),
        "Physical Activity Level": request.form.get("Physical Activity Level", type=int),
        "Screen Time per Day (hrs)": request.form.get("Screen Time per Day (hrs)", type=float),
        "Mood Swings Frequency": request.form.get("Mood Swings Frequency", type=int),
        "Panic Attacks Experience": request.form.get("Panic Attacks Experience", "No"),
        "Concentration Level": request.form.get("Concentration Level", type=int),
        "Intrusive Thoughts": request.form.get("Intrusive Thoughts", "No"),
        "Traumatic Experience History": request.form.get("Traumatic Experience History", "No"),
    }

    if email in df["email"].values:
        df.loc[df["email"] == email, new_response.keys()] = new_response.values()
    else:
        df = pd.concat([df, pd.DataFrame([new_response])], ignore_index=True)

    save_responses(df)
    predict_user_disorder(email, df, MODEL_PATH)
    return redirect(url_for("predictions"))

# Predictions Page
@app.route('/predictions')
def predictions():
    if "email" not in session:
        return redirect(url_for("login"))

    email = session["email"]
    df = load_responses()

    user_data = df[df["email"] == email]
    if user_data.empty:
        return render_template("prediction_result.html", error="User data not found!")

    predicted_disorders = {col: user_data.iloc[0][col] for col in user_data.columns[-8:] if user_data.iloc[0][col] == 1}

    disorder_descriptions = {
        "Anxiety Disorders": "A mental health disorder characterized by worry or fear that interferes with daily life.",
        "Bipolar Disorder": "Mood swings ranging from depressive lows to manic highs.",
        "Dissociative Disorders": "Disruptions in memory, identity, or awareness.",
        "ADHD": "Attention deficit, hyperactivity, and impulsiveness.",
        "PTSD": "Trouble recovering from traumatic events.",
        "Schizophrenia": "Distorted thinking and perception.",
        "OCD": "Obsessions and compulsive behaviors.",
        "Depression": "Persistent sadness and loss of interest."
    }

    disorders_with_desc = {d: disorder_descriptions[d] for d in predicted_disorders.keys()}

    return render_template("prediction_result.html", disorders=disorders_with_desc)

# Journal Page
@app.route('/journal', methods=['GET', 'POST'])
def journal():
    if "email" not in session:
        return redirect(url_for("login"))

    email = session["email"]
    journal_path = os.path.join(JOURNAL_DIR, f"{email}.txt")

    if request.method == "POST":
        entry = request.form.get("entry")
        with open(journal_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- Entry ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---\n{entry}\n")
        return redirect(url_for("chat"))

    entries = ""
    if os.path.exists(journal_path):
        with open(journal_path, "r", encoding="utf-8") as f:
            entries = f.read()

    return render_template("journal.html", entries=entries)

# Chat Page
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if "email" not in session:
        return redirect(url_for("login"))

    df = load_responses()
    user_data = df[df["email"] == session["email"]]
    disorders = [col for col in user_data.columns[-8:] if user_data.iloc[0][col] == 1] if not user_data.empty else []

    return render_template("chat.html", user_data={"disorders": disorders})


# Chat API
@app.route('/chat_api', methods=['POST'])
def chat_api():
    if "email" not in session:
        return jsonify({"response": "Please log in first!"})

    email = session["email"]
    user_message = request.form.get("message")
    response = get_chatbot_response(email, user_message)
    return jsonify({"response": response})

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
