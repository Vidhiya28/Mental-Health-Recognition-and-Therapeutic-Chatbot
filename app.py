from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pandas as pd
from keras.models import load_model
#from model import predict_user_disorder
from user_predictions.model import predict_user_disorder

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import register_user, verify_user

app = Flask(__name__, template_folder="templates")
app.secret_key = "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"  # Required for session management

SAVE_FOLDER = "user_predictions"
FILE_PATH = os.path.join(SAVE_FOLDER, "user_responses_new.csv")

model = load_model(os.path.join(SAVE_FOLDER, "mental_health_model.h5"))

COLUMN_NAMES = ["email", "Gender", "Age", "Academic Pressure", "Work Pressure", "Sleep Duration",
                "Have you ever had suicidal thoughts ?", "Work/Study Hours", "Financial Stress",
                "Social Activity Level", "Physical Activity Level", "Screen Time per Day (hrs)",
                "Mood Swings Frequency", "Panic Attacks Experience", "Concentration Level",
                "Intrusive Thoughts", "Traumatic Experience History"]

# Create CSV file if it doesn't exist
def create_responses_file():
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=COLUMN_NAMES)
        df.to_csv(FILE_PATH, index=False)

# Load existing responses
def load_responses():
    create_responses_file()
    return pd.read_csv(FILE_PATH)

# Save responses
def save_responses(df):
    df.to_csv(FILE_PATH, index=False)

# Convert Yes/No to binary
def binary_convert(value):
    return 1 if value.lower() == "yes" else 0

#Route: Home (Redirect to login if not authenticated)
@app.route('/')
def home():
    if "email" in session:
        return redirect(url_for("form"))
    return redirect(url_for("login"))

#Route: Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        if verify_user(email, password):
            session["email"] = email  # Store logged-in user in session
            return redirect(url_for("form"))
        else:
            return render_template("login.html", error="Invalid credentials!")

    return render_template("login.html")

#Route: Register Page
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

#Route: Logout
@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))

#Route: Render the Questionnaire Form
@app.route('/form')
def form():
    if "email" not in session:
        return redirect(url_for("login"))

    return render_template("form.html", email=session["email"])

#API to Handle Form Submissions
@app.route('/submit', methods=['POST'])
def submit():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    email = session["email"]  # Use logged-in user's email
    df = load_responses()

    # Get form data
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

    # Check if user already exists and update
    if email in df["email"].values:
        df.loc[df["email"] == email, new_response.keys()] = new_response.values()
    else:
        df = pd.concat([df, pd.DataFrame([new_response])], ignore_index=True)

    save_responses(df)  # Save updated data
    predicted_scores = predict_user_disorder(email, df, model)
    return jsonify({
        "message": "Response saved successfully!",
        "email": email,
        "predictions": [float(score) for score in predicted_scores]  
    })

if __name__ == '__main__':
    app.run(debug=True)
