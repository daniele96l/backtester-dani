import requests
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("/Users/danieleligato/PycharmProjects/DaniBacktester/portfoliopilot-99523-firebase-adminsdk-fbsvc-e645929e12.json")  # Use your service account key
firebase_admin.initialize_app(cred)

# Firestore instance
db = firestore.client()

class FirebaseAuthTest:
    def __init__(self, api_key):
        self.api_key = api_key
        self.auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        self.signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"

    def login(self, email, password):
        """Login using email and password to get Firebase ID Token"""
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            response = requests.post(self.auth_url, json=payload)
            if response.status_code == 200:
                id_token = response.json().get('idToken')
                return id_token
            else:
                error_message = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"Login failed: {error_message}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error during login: {e}")
            return None

    def register(self, email, password):
        """Register a new user using email and password"""
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            response = requests.post(self.signup_url, json=payload)
            if response.status_code == 200:
                id_token = response.json().get('idToken')
                # After registration, save the user data to Firestore
                self.save_user_data(email, mode="mode 2")  # By default, "mode 2"
                return id_token
            else:
                error_message = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"Registration failed: {error_message}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error during registration: {e}")
            return None

    def save_user_data(self, email, mode="mode 2"):
        """Save user data including mode status to Firestore"""
        user_ref = db.collection('users').document(email)  # Using email as unique ID
        user_ref.set({
            'mode': mode
        })
        print(f"User data saved: {email} - Mode: {mode}")

    def get_user_status(self, email):
        """Get user's mode from Firestore. If not found, create a document."""
        user_ref = db.collection('users').document(email)
        user_doc = user_ref.get()

        if user_doc.exists:
            return user_doc.to_dict().get('mode', "mode 2")  # Default to "mode 2" if not found
        else:
            # If no user document exists, create one with default mode as "mode 2"
            print(f"No user data found for {email}. Creating new user document.")
            self.save_user_data(email, mode="mode 2")
            return "mode 2"

    def upgrade_to_mode_1(self, email):
        """Change user's status to mode 1 in Firestore"""
        user_ref = db.collection('users').document(email)
        user_ref.update({
            'mode': "mode 1"
        })
        print(f"{email} is now in Mode 1!")


# Example usage
if __name__ == '__main__':
    firebase_api_key = "x"  #

    firebase_auth = FirebaseAuthTest(firebase_api_key)

    action = input("Enter 'register' to register a new user or 'login' to login: ").strip().lower()

    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()

    if action == 'register':
        token = firebase_auth.register(email, password)
        if token:
            print(f"Registration successful! ID Token: {token}")
        else:
            print("Registration failed.")

    elif action == 'login':
        token = firebase_auth.login(email, password)
        if token:
            print(f"Login successful! ID Token: {token}")
            # Check user status (mode)
            user_mode = firebase_auth.get_user_status(email)
            print(f"{email} is in {user_mode}.")

            upgrade_option = input("Do you want to switch to Mode 1? (yes/no): ").strip().lower()
            if upgrade_option == 'yes':
                firebase_auth.upgrade_to_mode_1(email)
        else:
            print("Login failed.")

    else:
        print("Invalid action. Please enter 'register' or 'login'.")

