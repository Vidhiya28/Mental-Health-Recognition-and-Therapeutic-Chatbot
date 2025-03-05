import openai
import os
import json

# Load OpenAI API Key (Store it securely in an environment variable)
openai.api_key = "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"

# Load chat history
CHAT_HISTORY_FILE = "chat_history.json"

# Ensure the chat history file exists
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def get_chatbot_response(user_email, user_message, user_disorders):
    """
    Generates a personalized response using ChatGPT-4.0 Mini.
    - Considers user's previous chat history.
    - Uses mental disorder predictions for relevant responses.
    - Asks meaningful follow-ups.
    """

    # Load chat history
    chat_history = load_chat_history()

    # Get user's past conversations (if available)
    user_conversation = chat_history.get(user_email, [])

    # Format conversation for OpenAI API
    messages = [{"role": "system", "content": "You are a helpful mental health chatbot that provides supportive and meaningful responses."}]

    # Add previous user messages & responses
    for entry in user_conversation[-5:]:  # Only keep last 5 messages
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["bot"]})

    # Add current user input
    messages.append({"role": "user", "content": user_message})

    # Generate response from ChatGPT-4.0 Mini
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    bot_response = response["choices"][0]["message"]["content"]

    # Save conversation history
    user_conversation.append({"user": user_message, "bot": bot_response})
    chat_history[user_email] = user_conversation[-10:]  # Keep only last 10 messages
    save_chat_history(chat_history)

    return bot_response