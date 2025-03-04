import openai
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Set API key
openai.api_key = "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"

# Initialize sentiment analysis
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """Returns sentiment score (Positive, Negative, Neutral)."""
    score = sia.polarity_scores(text)
    if score['compound'] > 0.05:
        return "Positive"
    elif score['compound'] < -0.05:
        return "Negative"
    else:
        return "Neutral"

def chat_with_gpt(prompt, chat_history):
    """Chatbot with memory: sends previous messages along with new input."""
    chat_history.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=chat_history
    )

    bot_response = response["choices"][0]["message"]["content"].strip()
    chat_history.append({"role": "assistant", "content": bot_response})

    return bot_response
