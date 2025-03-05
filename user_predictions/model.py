import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler


train_df = pd.read_csv("user_predictions\\Dataset_after_prediction.csv")

user_responses_df = pd.read_csv("user_predictions\\user_responses_new.csv")

feature_columns = ["Academic Pressure", "Work Pressure", "Sleep Duration",
                   "Have you ever had suicidal thoughts ?", "Work/Study Hours",
                   "Financial Stress", "Social Activity Level", "Physical Activity Level",
                   "Screen Time per Day (hrs)", "Mood Swings Frequency", "Panic Attacks Experience",
                   "Concentration Level", "Intrusive Thoughts", "Traumatic Experience History"]

target_columns = ["BDI_Score", "GAD7_Score", "PANSS_Score", "MDQ_Score", "YBOCS_Score",
                  "ASRS_Score", "PCL5_Score", "DES2_Score", "Anxiety Disorders", "Bipolar Disorder",
                  "Dissociative Disorders", "ADHD", "PTSD", "Schizophrenia", "OCD", "Depression"]


# Ensure target columns exist before updating
for column in target_columns:
    if column not in user_responses_df.columns:
        user_responses_df[column] = np.nan

X_train = train_df[feature_columns]
y_train = train_df[target_columns]

X_train = X_train.replace([np.inf, -np.inf], np.nan)  # Convert infinite values to NaN
X_train = X_train.fillna(X_train.median())  # Replace NaN with column median

#Normalize Features using MinMaxScaler
scaler = MinMaxScaler()
X_train = scaler.fit_transform(X_train)  # Scales data between 0 and 1
y_train = y_train.fillna(0)


# Define the Neural Network Model
model = keras.Sequential([
    layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),  # Input layer
    layers.Dense(32, activation='relu'),  # Hidden layer
    layers.Dense(len(target_columns), activation='linear')  # Output layer (linear for regression)
])

# Compile Model with Mean Squared Error (MSE)
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

# Train the Model
model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=1)

# Save the trained model
model.save("mental_health_model.h5")


#disorder prediction for the logged in user
def predict_user_disorder(email, user_responses_df, model):
    user_row = user_responses_df[user_responses_df["email"] == email]
    if user_row.empty:
        return "User not found."

    user_features = user_row[feature_columns].values.reshape(1, -1)

    # Normalize the features using the previously fitted scaler
    user_features = scaler.transform(user_features)

    # Predict disorder scores using the trained model
    predicted_scores = model.predict(user_features).flatten()
    score_predictions = predicted_scores[:8]  # First 8 are scores

    # Convert disorders (last 8 values) to binary (0 or 1)
    disorder_predictions = [1 if score >= 0.5 else 0 for score in predicted_scores[8:]]
    final_predictions = list(score_predictions) + disorder_predictions

    for i, column in enumerate(target_columns):
        user_responses_df.at[user_row.index[0], column] = final_predictions[i]
    user_responses_df.to_csv("user_predictions/user_responses.csv", index=False)

    return final_predictions
