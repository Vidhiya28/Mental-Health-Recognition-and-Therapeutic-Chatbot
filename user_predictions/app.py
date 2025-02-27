from flask import Flask, request, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)

# File path for storing responses
FILE_PATH = "user_responses.csv"

# Define dataset columns
COLUMN_NAMES = ["id", "Gender", "Age", "Academic Pressure", "Work Pressure", "Sleep Duration",
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

# Assign a unique ID (28000-29000 range)
def generate_unique_id():
    df = load_responses()
    existing_ids = df["id"].tolist() if not df.empty else []
    available_ids = [i for i in range(28000, 29001) if i not in existing_ids]
    return available_ids[0] if available_ids else None

# Convert Yes/No to binary
def binary_convert(value):
    return 1 if value.lower() == "yes" else 0

# Render the questionnaire HTML form
@app.route('/')
def form():
    return render_template("form.html", user_id=generate_unique_id())

# API to handle form submissions
@app.route('/submit', methods=['POST'])
def submit():
    df = load_responses()

    # Get form data
    user_id = request.form.get("id", type=int)
    gender = request.form.get("Gender")
    age = request.form.get("Age", type=int)
    academic_pressure = request.form.get("Academic Pressure", type=int)
    work_pressure = request.form.get("Work Pressure", type=int)
    sleep_duration = request.form.get("Sleep Duration", type=float)
    suicidal_thoughts = binary_convert(request.form.get("Have you ever had suicidal thoughts ?", "No"))
    study_hours = request.form.get("Work/Study Hours", type=float)
    financial_stress = request.form.get("Financial Stress", type=int)
    social_activity = request.form.get("Social Activity Level", type=int)
    physical_activity = request.form.get("Physical Activity Level", type=int)
    screen_time = request.form.get("Screen Time per Day (hrs)", type=float)
    mood_swings = request.form.get("Mood Swings Frequency", type=int)
    panic_attacks = binary_convert(request.form.get("Panic Attacks Experience", "No"))
    concentration = request.form.get("Concentration Level", type=int)
    intrusive_thoughts = binary_convert(request.form.get("Intrusive Thoughts", "No"))
    trauma_history = binary_convert(request.form.get("Traumatic Experience History", "No"))

    # Create response dictionary
    new_response = {
        "id": user_id,
        "Gender": gender,
        "Age": age,
        "Academic Pressure": academic_pressure,
        "Work Pressure": work_pressure,
        "Sleep Duration": sleep_duration,
        "Have you ever had suicidal thoughts ?": suicidal_thoughts,
        "Work/Study Hours": study_hours,
        "Financial Stress": financial_stress,
        "Social Activity Level": social_activity,
        "Physical Activity Level": physical_activity,
        "Screen Time per Day (hrs)": screen_time,
        "Mood Swings Frequency": mood_swings,
        "Panic Attacks Experience": panic_attacks,
        "Concentration Level": concentration,
        "Intrusive Thoughts": intrusive_thoughts,
        "Traumatic Experience History": trauma_history,
    }

    # Check if user already exists and update
    if user_id in df["id"].values:
        df.loc[df["id"] == user_id, new_response.keys()] = new_response.values()
    else:
        df = pd.concat([df, pd.DataFrame([new_response])], ignore_index=True)

    # Save updated responses
    save_responses(df)

    return jsonify({"message": "Response saved successfully!", "user_id": user_id})

if __name__ == '__main__':
    app.run(debug=True)
