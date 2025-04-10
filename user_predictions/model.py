import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
import joblib

# Load the dataset
train_df = pd.read_csv("user_predictions/Dataset_after_prediction.csv")
user_responses_df = pd.read_csv("user_predictions/user_responses.csv")

# Define feature and target columns
feature_columns = [
    "Academic Pressure", "Work Pressure", "Sleep Duration",
    "Have you ever had suicidal thoughts ?", "Work/Study Hours",
    "Financial Stress", "Social Activity Level", "Physical Activity Level",
    "Screen Time per Day (hrs)", "Mood Swings Frequency", "Panic Attacks Experience",
    "Concentration Level", "Intrusive Thoughts", "Traumatic Experience History"
]

target_columns = [
    "BDI_Score", "GAD7_Score", "PANSS_Score", "MDQ_Score", "YBOCS_Score",
    "ASRS_Score", "PCL5_Score", "DES2_Score", "Anxiety Disorders", "Bipolar Disorder",
    "Dissociative Disorders", "ADHD", "PTSD", "Schizophrenia", "OCD", "Depression"
]

# Fill missing columns if needed
for column in target_columns:
    if column not in user_responses_df.columns:
        user_responses_df[column] = np.nan

# Prepare training data
X_train = train_df[feature_columns].replace([np.inf, -np.inf], np.nan).fillna(train_df[feature_columns].median())
y_train = train_df[target_columns].fillna(0)

# Normalize features
scaler = MinMaxScaler()
X_train = scaler.fit_transform(X_train)

# Save the scaler
joblib.dump(scaler, "scaler.pkl")

# Build the model
model = keras.Sequential([
    layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    layers.Dense(32, activation='relu'),
    layers.Dense(len(target_columns), activation='linear')
])

# Compile and train
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=1)

# Save the model
model.save("mental_health_model.h5")

# Prediction function
def predict_user_disorder(email, user_responses_df, model):
    from sklearn.preprocessing import MinMaxScaler
    scaler = joblib.load("scaler.pkl")

    user_row = user_responses_df[user_responses_df["email"] == email].copy()
    if user_row.empty:
        return "User not found."

    categorical_columns = [
        "Have you ever had suicidal thoughts ?", "Panic Attacks Experience",
        "Intrusive Thoughts", "Traumatic Experience History"
    ]
    for col in categorical_columns:
        if col in user_row.columns:
            user_row[col] = user_row[col].map({"Yes": 1, "No": 0})

    user_features = user_row[feature_columns].values.reshape(1, -1)
    user_features = scaler.transform(user_features)

    predicted_scores = model.predict(user_features).flatten()
    score_predictions = predicted_scores[:8]
    disorder_predictions = [1 if score >= 0.5 else 0 for score in predicted_scores[8:]]

    for i, column in enumerate(target_columns[:8]):
        user_responses_df.at[user_row.index[0], column] = score_predictions[i]
    for i, column in enumerate(target_columns[8:]):
        user_responses_df.at[user_row.index[0], column] = disorder_predictions[i]

    user_responses_df.to_csv("user_predictions/user_responses.csv", index=False)

    return list(score_predictions) + disorder_predictions
