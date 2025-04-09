import pandas as pd
import bcrypt

USER_DB = "users.csv"

# Create user database if missing
def create_user_db():
    try:
        df = pd.read_csv(USER_DB)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["email", "password"])
        df.to_csv(USER_DB, index=False)

def register_user(email, password):
    df = pd.read_csv(USER_DB)

    if email in df["email"].values:
        return False  # Email already exists

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = pd.DataFrame([[email, hashed_pw]], columns=["email", "password"])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_DB, index=False)
    return True

def verify_user(email, password):
    """Verifies user login by checking hashed password."""
    df = pd.read_csv(USER_DB)

    user_row = df[df["email"] == email]
    if user_row.empty:
        return False  # User not found

    hashed_pw = user_row.iloc[0]["password"]
    return bcrypt.checkpw(password.encode(), hashed_pw.encode())

create_user_db()  # Ensure user database exists
