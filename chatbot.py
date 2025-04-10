import os
import json
from huggingface_api import query_model

SYSTEM_PROMPT = """
You are an emotionally intelligent mental health assistant.

- Keep responses short (10–20 words) unless the user asks for insights.
- Be empathetic, caring, and attentive. Use past messages to show understanding.
- Listen deeply when users share emotional struggles. Don’t judge or rush to fix.
- Offer gentle reflection, motivational support (quotes, CBT, mindfulness), and practical coping strategies.
- Never diagnose, but help users notice emotional patterns and behaviors.
- Ask thoughtful, open-ended questions to guide self-awareness.
- Gently challenge negative self-beliefs and offer healthier perspectives.
- Celebrate wins and encourage self-kindness.
- Speak confidently. Only suggest professional help in extreme cases.

Your goal: Help users feel heard, supported, and empowered. Always be here for them.
"""

CONVO_DIR = "user_predictions/conversations"
os.makedirs(CONVO_DIR, exist_ok=True)

def load_conversation(email):
    path = os.path.join(CONVO_DIR, f"{email}_chat.json")
    if os.path.exists(path):
        with open(path, "r") as file:
            return json.load(file)
    return []

def save_conversation(email, conversation):
    path = os.path.join(CONVO_DIR, f"{email}_chat.json")
    with open(path, "w") as file:
        json.dump(conversation, file)

def get_chatbot_response(email, user_message, user_disorders=[]):
    conversation = load_conversation(email)

    conversation.append({"role": "user", "content": user_message})

    # Build plain natural prompt (no [INST] format)
    prompt = f"{SYSTEM_PROMPT.strip()}\n\n"
    for msg in conversation[-5:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"
    prompt += "Assistant:"

    print("Sending prompt:", prompt)  # optional for debug

    response = query_model(prompt)

    conversation.append({"role": "assistant", "content": response})
    save_conversation(email, conversation)

    return response
