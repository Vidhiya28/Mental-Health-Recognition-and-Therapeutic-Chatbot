import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://api.together.xyz/v1/completions"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

def query_model(prompt):
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.7,
        "top_p": 0.9,
        "stop": ["User:", "Assistant:"]
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    # Debug if failed
    if response.status_code != 200:
        print("🔴 Together API Error:", response.status_code)
        print("Response:", response.text)
        response.raise_for_status()

    return response.json()["choices"][0]["text"].strip()

