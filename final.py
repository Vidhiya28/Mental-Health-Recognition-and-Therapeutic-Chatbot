from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from chatbot import chat_with_gpt, analyze_sentiment
from user_data import get_user_data
from database import register_user, verify_user

app = Flask(__name__)
app.secret_key = "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"
chat_history = []  # Stores conversation history

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

    user_data = get_user_data(session["email"])
    return render_template("index.html", user_data=user_data)

# Route: Chatbot API
@app.route('/chat_api', methods=['POST'])
def chat_api():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"})

    user_input = request.form['message']
    sentiment = analyze_sentiment(user_input)
    response = chat_with_gpt(user_input, chat_history)

    if sentiment == "Negative":
        response += " 🫂 It seems like you're feeling down. I'm here for you."
    elif sentiment == "Positive":
        response += " 😊 I'm glad to hear that!"

    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": response})

    return jsonify({"response": response})

# Route: Logout
@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)
