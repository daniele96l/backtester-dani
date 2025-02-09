from dash import dcc, html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from FirebaseAuth import FirebaseAuth
from config import PUBLIC_KEY


def PopupManager(app):
    modal = dbc.Modal(
        [
            dbc.ModalHeader("Accesso / Registrazione"),
            dbc.ModalBody(
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

    # Nuovo callback per gestire l'invio del form
    @app.callback(
        Output("auth-feedback", "children"),
        [Input("submit-auth", "n_clicks")],
        [
            State("toggle-auth", "value"),
            State("username", "value"),
            State("password", "value"),
            State("gdpr-checkbox", "value")
        ]
    )
    def gestisci_auth(n_clicks, tipo_auth, username, password, gdpr_accettato):
        firebase_auth = FirebaseAuth(PUBLIC_KEY)

        """Gestisce l'invio del form di login/registrazione."""
        if n_clicks is None:
            return ""

        if not username or not password:
            return html.Div("Per favore, compila tutti i campi", style={"color": "red"})

        # Gestione Login
        if tipo_auth == "login":
            stato_login = firebase_auth.login(username, password)
            return html.Div(stato_login, style={"color": "green"})

        # Gestione Registrazione
        elif tipo_auth == "register":
            if not gdpr_accettato:
                return html.Div("Devi accettare i termini GDPR per registrarti", style={"color": "red"})
            else:
                stato_registrazione = firebase_auth.register(username, password)

            return html.Div(stato_registrazione, style={"color": "green"})

    return modal

