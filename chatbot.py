import openai
import os
import json


OPENAI_API_KEY = "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"
client = openai.OpenAI(api_key=OPENAI_API_KEY)

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
    '''
    Generates a personalized response using ChatGPT-4.0 Mini.
    - Considers user's previous chat history.
    - Uses mental disorder predictions for relevant responses.
    - Asks meaningful follow-ups.
    '''

    chat_history = load_chat_history()
    user_conversation = chat_history.get(user_email, [])

    disorder_info = (
        f"This user has been identified with: {', '.join(user_disorders)}."
        if user_disorders else 
        "This user has no identified mental health disorders."
    )

    system_message = {
        "role": "system",
        "content": (
            "You are a mental health chatbot providing supportive, insightful, and personalized responses. "
            f"{disorder_info} "
            "Provide meaningful guidance, ask relevant follow-up questions, and offer mental health tips."
        )
    }

    # Add chat history (only last 5 messages for context)
    messages = [system_message]
    for entry in user_conversation[-5:]:
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["bot"]})

    # Add the latest user message
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        bot_response = response["choices"][0]["message"]["content"]

        user_conversation.append({"user": user_message, "bot": bot_response})
        chat_history[user_email] = user_conversation[-10:]
        save_chat_history(chat_history)

        return bot_response
    
    except Exception as e:
        print(f"Error in OpenAI API: {e}")  # Debugging print statement
        return "I'm having trouble responding right now. Try again later."