# 🧠 Mental Health Recognition and Therapeutic Chatbot System

## 📌 Project Intro
In today’s fast-paced digital world, young people between the ages of 15 to 25 face overwhelming academic pressure, social comparison, identity struggles, and emotional isolation—often without knowing where to turn. 
Many suffer in silence due to stigma, fear of judgment, or lack of access to affordable therapy. 

This project is an **AI-powered mental health support platform** offers a safe, non-judgmental space where youth can express their feelings, receive empathetic support, and build emotional resilience. It bridges the gap between awareness and action, empowering them to seek help early, understand themselves better, and prioritize mental well-being in a way that feels accessible, private, and personal.
It is designed to identify potential mental health disorders through user-submitted questionnaire and provide **empathetic, therapeutic conversations** through a chatbot.

Using machine learning, it predicts **8 different mental disorders and scores**, and then dynamically tailors chatbot interactions based on the results. The system also includes tools like **journaling** and **conversation memory** to enhance emotional support and build a more personalized experience.

> ✅ **Outcome**: A fully functional web application that predicts disorders, engages users with supportive dialogues, and serves as a digital mental wellness companion — especially for youth aged **15–25**, who are often vulnerable but hesitant to seek help.

---

## 💡 Key Features

- 🧠 **Mental Health Disorder Prediction** using an MLP neural network (BDI, GAD-7, PTSD, OCD, etc.)
- 🤖 **AI Chatbot** powered with conversation memory
- 📓 **Personal Journal Page** to allow users to express thoughts and emotions
- 🌈 **Mood-based Responses** tailored using previous inputs and predictions
- 🧾 **User Authentication & Secure Session Handling**
- 📁 **Dynamic Form Interface** to collect mental health indicators
- 📈 **Visualization Ready Predictions** for research and reporting use

---

## 🛠️ Challenges Faced

| Challenge                         | How It Was Tackled                                                                 |
|----------------------------------|------------------------------------------------------------------------------------|
| Balancing Empathy in Chatbot     | Used detailed prompt engineering, memory-based conversation design                |
| Class Imbalance                          | Used stratified sampling and class-weighted loss functions to address skewed disorder distributions     |
| Feature Engineering for Mixed Data       | Engineered features from categorical and continuous survey inputs; standardized scales with MinMaxScaler |
| Balancing Empathy in Chatbot     | Used detailed prompt engineering, memory-based conversation design                |
| Multi-label Classification Complexity    | Designed custom loss and evaluation pipeline to handle multiple overlapping disorder labels             |
| UI/UX Integration                | Built simple and clean HTML interfaces; used Flask for routing and user session control |

---

## 🚀 Future Improvements

- 📊 **Analytics Dashboard** to monitor trends in mental health patterns
- 📱 **Mobile Application Version** for greater accessibility
- 🧠 **Mental Health Resource Recommender** based on disorders detected

---

## 📸 Implementation Screenshots

![image](https://github.com/user-attachments/assets/5b2ce3f2-225c-4598-8152-255c94df2b95)

![image](https://github.com/user-attachments/assets/f21ba7c1-c708-4f83-8740-8781c1f75035)

---

## ⚙️ How to Install and Run the Project

```bash
# Clone the repository
git clone https://github.com/your-repo/mental-health-chatbot.git
cd mental-health-chatbot

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate    # For Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask app
python app.py

```

---

## 👥 Contributors

- @Tej-00 - Project Lead Developer, Model Development, Data Preprocessing, Model Trainer.
- @vidhiya28 – UI/UX developer, Integrated ML outputs, Performance Testing and documentation.

---

_This project supports awareness and conversation around mental health. It is not a substitute for professional care._

