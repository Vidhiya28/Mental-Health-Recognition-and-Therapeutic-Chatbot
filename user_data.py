import pandas as pd

CSV_FILE = "user_responses.csv"

def get_user_data(user_id):
    """Fetch user responses from CSV file based on User ID."""
    df = pd.read_csv(CSV_FILE)

    user_row = df[df["id"] == int(user_id)]
    if not user_row.empty:
        return user_row.iloc[0].to_dict()  # Convert row to dictionary
    return {"error": "User not found"}
