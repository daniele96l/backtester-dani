import requests
import firebase_admin
from firebase_admin import credentials, firestore
from config import KEY_PATH
PUBLIC_KEY = "AIzaSyBX_AH1_hAdmnzDHKcGW83tcHHJKat1Lps"

# Initialize Firebase Admin SDK
cred = credentials.Certificate(KEY_PATH)
firebase_admin.initialize_app(cred)

db = firestore.client()
class FirebaseAuth:
    def __init__(self, api_key):
        self.api_key = api_key
        self.auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        self.signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"

    def login(self, email, password):
        """Effettua il login di un utente e restituisce il token ID con un messaggio di successo."""
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(self.auth_url, json=payload)

        if response.status_code == 200:
            return f"Login effettuato con successo per {email}. Token restituito.", True
        else:
            error_message = response.json().get('error', {}).get('message', 'Errore sconosciuto')
            detailed_error = self.get_error_details(error_message)
            print(f"Login fallito: {detailed_error}")
            return detailed_error, False

    def register(self, email, password, mode="mode 2"):
        """Registra un nuovo utente e salva i suoi dati in Firestore, con un messaggio di successo."""
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(self.signup_url, json=payload)

        if response.status_code == 200:
            self.save_user_data(email, mode)
            return f"Registrazione effettuata con successo per {email}.", True
        else:
            error_message = response.json().get('error', {}).get('message', 'Errore sconosciuto')
            detailed_error = self.get_error_details(error_message)
            return detailed_error,False

    def save_user_data(self, email, mode):
        """Saves user data to Firestore."""
        db.collection('users').document(email).set({'mode': mode})
        print(f"User {email} saved with mode {mode}.")

    def get_user_status(self, email):
        """Retrieves the user's mode from Firestore, creating a new document if necessary."""
        user_ref = db.collection('users').document(email)
        user_doc = user_ref.get()

        if user_doc.exists:
            return user_doc.to_dict().get('mode', "mode 2")
        else:
            self.save_user_data(email, "mode 2")
            return "mode 2"

    def upgrade_to_mode_1(self, email):
        """Upgrades the user to mode 1."""
        db.collection('users').document(email).update({'mode': "mode 1"})
        print(f"{email} is now in Mode 1!")

    def get_error_details(self, error_message):
        """Fornisce una descrizione dettagliata dell'errore."""
        error_dict = {
            'INVALID_EMAIL': "L'indirizzo email fornito non è valido. Controlla che l'email sia corretta.",
            'INVALID_PASSWORD': "La password inserita è errata. Assicurati di inserire la password corretta.",
            'USER_DISABLED': "L'account utente è stato disabilitato. Contatta l'amministratore.",
            'EMAIL_EXISTS': "L'email fornita è già associata a un altro account. Prova a registrarti con un'email diversa.",
            'WEAK_PASSWORD : Password should be at least 6 characters': "La password è troppo debole. Scegli una password più sicura con almeno 6 caratteri.",
            'EMAIL_NOT_FOUND': "Non esiste un account associato a questa email. Verifica l'email o registrati.",
            'INVALID_LOGIN_CREDENTIALS': "Le credenziali di login sono errate. Controlla l'email e la password.",
            'UNKNOWN_ERROR': "Si è verificato un errore sconosciuto. Riprova più tardi.",
        }

        return error_dict.get(error_message, "Errore sconosciuto: " + error_message)
