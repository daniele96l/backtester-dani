from dash import dcc, html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from FirebaseAuth import FirebaseAuth
from config import PUBLIC_KEY


def PopupManager(app):
    modal = dbc.Modal(
        [
            #dcc.Store(id='login-state', storage_type='local'),
            dbc.ModalHeader("Accesso / Registrazione"),
            dbc.ModalBody(
                html.Div([
                    # Login status message
                    html.Div(id="login-status"),
                    # Container for login/register form
                    html.Div([
                        # Alterna tra Login e Registrazione
                        dbc.RadioItems(
                            id="toggle-auth",
                            options=[
                                {"label": "Accedi", "value": "login"},
                                {"label": "Registrati", "value": "register"},
                            ],
                            value="login",
                            inline=True,
                            className="mb-3",
                        ),
                        # Campo Username
                        html.Label("Nome utente"),
                        dcc.Input(id="username", type="text", placeholder="Inserisci il nome utente"),
                        html.Br(),
                        # Campo Password
                        html.Label("Password"),
                        dcc.Input(id="password", type="password", placeholder="Inserisci la password"),
                        html.Br(),
                        # Checkbox GDPR (solo per Registrazione)
                        dbc.Checkbox(
                            id="gdpr-checkbox",
                            label="Accetto i termini GDPR",
                            className="mt-2",
                        ),
                        html.Br(),
                        # Bottone di invio
                        dbc.Button("Invia", id="submit-auth", color="primary", className="mt-2"),
                        # Div per messaggi di feedback
                        html.Div(id="auth-feedback", className="mt-2")
                    ], id="auth-form"),
                    # Logout button container
                    html.Div([
                        html.H5("Benvenuto!", className="mb-3"),
                        dbc.Button("Logout", id="logout-button", color="danger", className="mt-2"),
                    ], id="logout-container", style={"display": "none"}),
                ], id="contenuto-modale")
            ),
            dbc.ModalFooter(
                dbc.Button("Chiudi", id="close-modal", className="ml-auto", n_clicks=0)
            ),
        ],
        id="login-modal",
        is_open=False,
    )

    # Callback per gestire la visibilità del checkbox e lo stato del bottone
    @app.callback(
        [Output("gdpr-checkbox", "style"), Output("submit-auth", "disabled")],
        [Input("toggle-auth", "value"), Input("gdpr-checkbox", "value")]
    )
    def aggiorna_elementi(tipo_auth, gdpr_selezionato):
        """Mostra il checkbox GDPR solo per la registrazione e abilita il bottone di invio se selezionato."""
        stile_gdpr = {"display": "block"} if tipo_auth == "register" else {"display": "none"}
        bottone_disabilitato = not gdpr_selezionato if tipo_auth == "register" else False
        return stile_gdpr, bottone_disabilitato

    # Callback to handle form visibility based on login state
    @app.callback(
        [
            Output("auth-form", "style"),
            Output("logout-container", "style"),
            Output("login-status", "children")
        ],
        [Input("login-state", "data")]
    )
    def update_auth_view(login_state):
        if login_state and login_state.get("logged_in"):
            return (
                {"display": "none"},  # Hide login form
                {"display": "block"},  # Show logout button
                f"Logged in as: {login_state.get('username')}"  # Show username
            )
        return (
            {"display": "block"},  # Show login form
            {"display": "none"},  # Hide logout button
            ""  # Clear login status
        )

    @app.callback(
        [Output("auth-feedback", "children"), Output("login-state", "data")],
        [Input("submit-auth", "n_clicks"), Input("logout-button", "n_clicks")],
        [
            State("toggle-auth", "value"),
            State("username", "value"),
            State("password", "value"),
            State("gdpr-checkbox", "value"),
            State("login-state", "data")
        ]
    )
    def gestisci_auth(submit_clicks, logout_clicks, tipo_auth, username, password, gdpr_accettato, current_login_state):
        firebase_auth = FirebaseAuth(PUBLIC_KEY)
        ctx = callback_context

        if not ctx.triggered:
            return "", current_login_state

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Handle logout
        if trigger_id == "logout-button":
            return html.Div("Logout effettuato con successo", style={"color": "green"}), None

        # Handle login/register
        if trigger_id == "submit-auth":
            if not username or not password:
                return html.Div("Per favore, compila tutti i campi", style={"color": "red"}), None

            # Gestione Login
            if tipo_auth == "login":
                stato_login, logged = firebase_auth.login(username, password)
                if logged:
                    return html.Div(stato_login, style={"color": "green"}), {"logged_in": True, "username": username}
                else:
                    return html.Div(stato_login, style={"color": "red"}), None

            # Gestione Registrazione
            elif tipo_auth == "register":
                if not gdpr_accettato:
                    return html.Div("Devi accettare i termini GDPR per registrarti", style={"color": "red"}), None
                else:
                    stato_registrazione, registered = firebase_auth.register(username, password)
                    if registered:
                        return html.Div(stato_registrazione, style={"color": "green"}), {"logged_in": True,
                                                                                         "username": username}
                    else:
                        return html.Div(stato_registrazione, style={"color": "red"}), None

        return "", current_login_state

    return modal

