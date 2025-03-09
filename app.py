from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
import time
from keras.models import load_model

from chatbot import get_chatbot_response
from database import register_user, verify_user
from user_predictions.model import predict_user_disorder  

app = Flask(__name__, template_folder="templates") 
app.secret_key = "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"

'''# Update file paths to match new location inside `chatbot/`
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get `chatbot/` folder path
USER_RESPONSES_PATH = os.path.join(BASE_DIR, "../user_predictions/user_responses.csv")
MODEL_PATH = os.path.join(BASE_DIR, "../user_predictions/mental_health_model.h5")
'''
# Load ML model
SAVE_FOLDER = "user_predictions"
USER_RESPONSES_PATH = os.path.join(SAVE_FOLDER, "user_responses.csv")
MODEL_PATH = load_model(os.path.join(SAVE_FOLDER, "mental_health_model.h5"))

# Caching responses to reduce file I/O
cached_responses = None
last_load_time = 0

def load_responses():
    """Load user responses with caching."""
    global cached_responses, last_load_time
    if cached_responses is None or time.time() - last_load_time > 30:  # Reload every 30 sec
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

# Home route (redirects based on login status)
@app.route('/')
def home():
    if "email" in session:
        return redirect(url_for("chat"))
    return redirect(url_for("login"))

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        if verify_user(email, password):
            session["email"] = email

            df = load_responses()
            user_exists = not df[df["email"] == email].empty

            if user_exists:
                return redirect(url_for("chat"))  # Redirect to chatbot if responses exist
            else:
                return redirect(url_for("form"))  # Else, go to form

        else:
            return render_template("login.html", error="Invalid credentials!")
        
    return render_template("login.html")

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        if register_user(email, password):
            return redirect(url_for("login"))  # Redirect to login page after registration
        else:
            return render_template("register.html", error="Email already exists!")

    return render_template("register.html")

# Logout
@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))

# Form Page
@app.route('/form', methods=['GET', 'POST'])
def form():
    if "email" not in session:
        return redirect(url_for("login"))  # Redirect to login if not authenticated

    email = session["email"]
    df = load_responses()

    if request.method == "POST":  # When the user submits the form
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

        save_responses(df)  # Save updated responses

        return redirect(url_for("predictions"))

    # **GET request: Load previous user responses if available**
    user_data = df[df["email"] == email].to_dict(orient="records")
    user_data = user_data[0] if user_data else {}

    return render_template("form.html", email=email, user_data=user_data)

@app.route('/submit', methods=['POST'])
def submit():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    email = session["email"]  
    df = load_responses()

    # Collect form data
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

    # Save response
    if email in df["email"].values:
        df.loc[df["email"] == email, new_response.keys()] = new_response.values()
    else:
        df = pd.concat([df, pd.DataFrame([new_response])], ignore_index=True)

    save_responses(df)
    predict_user_disorder(email, df, MODEL_PATH)
    return redirect(url_for("predictions"))

@app.route('/predictions')
def predictions():
    if "email" not in session:
        return redirect(url_for("login"))

    email = session["email"]
    df = load_responses()

    user_data = df[df["email"] == email]
    if user_data.empty:
        return render_template("prediction_result.html", error="User data not found!")

    # Extract disorder predictions (Binary values 1 or 0)
    predicted_disorders = {col: user_data.iloc[0][col] for col in user_data.columns[-8:] if user_data.iloc[0][col] == 1}

    # Disorder Descriptions (Modify descriptions as needed)
    disorder_descriptions = {
        "Anxiety Disorders": "A mental health disorder characterized by feelings of worry, anxiety, or fear that are strong enough to interfere with daily activities.",
        "Bipolar Disorder": "A disorder associated with episodes of mood swings ranging from depressive lows to manic highs.",
        "Dissociative Disorders": "Conditions involving disruptions or breakdowns of memory, awareness, identity, or perception.",
        "ADHD": "A chronic condition including attention difficulty, hyperactivity, and impulsiveness.",
        "PTSD": "A disorder in which a person has difficulty recovering after experiencing or witnessing a terrifying event.",
        "Schizophrenia": "A serious mental disorder affecting a person’s ability to think, feel, and behave clearly.",
        "OCD": "A disorder where people have recurring, unwanted thoughts (obsessions) and behaviors (compulsions).",
        "Depression": "A mood disorder causing a persistent feeling of sadness and loss of interest."
    }

    # Create a dictionary with disorder names and their descriptions
    disorders_with_desc = {disorder: disorder_descriptions[disorder] for disorder in predicted_disorders.keys()}

    return render_template("prediction_result.html", disorders=disorders_with_desc)

# Chatbot Page
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
    user_message = request.form.get("message")

    df = load_responses()
    user_data = df[df["email"] == email]
    user_disorders = [col for col in user_data.columns[-8:] if user_data.iloc[0][col] == 1] if not user_data.empty else []

    print(f"Received message: {user_message}") 
    
    chatbot_response = get_chatbot_response(email, user_message, user_disorders)

    return jsonify({"response": chatbot_response})

if __name__ == '__main__':
    app.run(debug=True)

