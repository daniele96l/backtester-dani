from dash import dcc, html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from FirebaseAuth import FirebaseAuth

PUBLIC_KEY = "AIzaSyBX_AH1_hAdmnzDHKcGW83tcHHJKat1Lps"


def PopupManager(app):
    # Stili personalizzati
    CUSTOM_STYLES = {
        "modal": {
            "max-width": "450px",
            "border-radius": "12px",
            "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
            "position": "absolute",
            "top": "50%",
            "left": "50%",
            "transform": "translate(-50%, -50%)",
            "margin": "0",
        },
        "header": {
            "background-color": "#f8f9fa",
            "border-bottom": "1px solid #e9ecef",
            "border-radius": "12px 12px 0 0",
            "padding": "1.5rem",
        },
        "input": {
            "width": "100%",
            "padding": "0.75rem",
            "margin": "0.5rem 0",
            "border": "1px solid #ced4da",
            "border-radius": "6px",
            "font-size": "1rem",
        },
        "button": {
            "width": "100%",
            "padding": "0.75rem",
            "font-weight": "500",
            "text-transform": "uppercase",
            "letter-spacing": "0.5px",
        },
        "label": {
            "font-weight": "500",
            "color": "#495057",
            "margin-top": "1rem",
        },
        "tabs": {
            "margin-bottom": "1.5rem",
        }
    }

    modal = dbc.Modal(
        [
            dbc.ModalHeader(
                html.H4("Accesso / Registrazione", style={"margin-bottom": "0"}),
                style=CUSTOM_STYLES["header"],
                close_button=False,
            ),
            dbc.ModalBody(
                html.Div([
                    # Status di login con stile
                    html.Div(
                        id="login-status",
                        style={"text-align": "center", "margin-bottom": "1rem", "color": "#0d6efd"},
                    ),
                    html.H6(
                        "Registradoti nel futuro avrai la possibilità di salvare i tuoi portafogli personalizzati, registrati ora per avere questa features non appena diventa disponibile",
                        id="registration-info",
                        style={"color": "#6c757d"}
                    ),

                    # Form di autenticazione
                    html.Div([
                        # Tabs per login/register
                        dbc.Tabs(
                            [
                                dbc.Tab(label="Accedi", tab_id="login"),
                                dbc.Tab(label="Registrati", tab_id="register"),
                            ],
                            id="toggle-auth",
                            active_tab="login",
                            style=CUSTOM_STYLES["tabs"],
                        ),

                        # Campi del form
                        html.Div([
                            html.Label("Email", style=CUSTOM_STYLES["label"]),
                            dcc.Input(
                                id="username",
                                type="email",
                                placeholder="Inserisci la tua email",
                                style=CUSTOM_STYLES["input"],
                            ),

                            html.Label("Password", style=CUSTOM_STYLES["label"]),
                            dcc.Input(
                                id="password",
                                type="password",
                                placeholder="Inserisci la password",
                                style=CUSTOM_STYLES["input"],
                            ),

                            # Container GDPR e Termini
                            html.Div([
                                dbc.Checkbox(
                                    id="gdpr-checkbox",
                                    label=html.Span([
                                        "Ho letto e accetto l'informativa sulla privacy e il trattamento dei dati personali",
                                    ]),
                                    className="mb-3",
                                ),
                                html.A(
                                    "Termini e Condizioni",
                                    href="https://danieleligato-eng.notion.site/Termini-e-Condizioni-196922846a1680ab8686d1a817717ae2",
                                    target="_blank",
                                    className="d-block text-primary mb-3",
                                    style={"text-decoration": "none"},
                                ),
                            ], id="gdpr-terms-container", style={"margin": "1rem 0"}),

                            # Feedback per errori/successi
                            html.Div(
                                id="auth-feedback",
                                style={"margin": "1rem 0", "text-align": "center"},
                            ),

                            # Bottone di invio
                            dbc.Button(
                                "Invia",
                                id="submit-auth",
                                color="primary",
                                style=CUSTOM_STYLES["button"],
                            ),
                        ], style={"padding": "1rem 0"}),
                    ], id="auth-form"),

                    # Container logout
                    html.Div([
                        html.H5(
                            "Benvenuto!",
                            className="text-center mb-4",
                            style={"color": "#0d6efd"},
                        ),
                        dbc.Button(
                            "Logout",
                            id="logout-button",
                            color="danger",
                            style=CUSTOM_STYLES["button"],
                        ),
                    ], id="logout-container", style={"display": "none"}),
                ], id="contenuto-modale", style={"padding": "1rem"}),
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Chiudi",
                    id="close-modal",
                    color="secondary",
                    style={"width": "auto"},
                ),
                style={"background-color": "#f8f9fa", "border-top": "1px solid #e9ecef"},
            ),
        ],
        id="login-modal",
        is_open=False,
        style=CUSTOM_STYLES["modal"],
    )

    @app.callback(
        [
            Output("gdpr-terms-container", "style"),
            Output("submit-auth", "disabled")
        ],
        [Input("toggle-auth", "active_tab"), Input("gdpr-checkbox", "value")]
    )
    def aggiorna_elementi(tipo_auth, gdpr_selezionato):
        stile_base = {"margin": "1rem 0"}
        if tipo_auth == "register":
            stile_base["display"] = "block"
        else:
            stile_base["display"] = "none"

        bottone_disabilitato = not gdpr_selezionato if tipo_auth == "register" else False
        return stile_base, bottone_disabilitato

    @app.callback(
        [
            Output("auth-form", "style"),
            Output("logout-container", "style"),
            Output("login-status", "children"),
            Output("registration-info", "style"),  # New output for H6 visibility
        ],
        [Input("login-state", "data")]
    )
    def update_auth_view(login_state):
        if login_state and login_state.get("logged_in"):
            return (
                {"display": "none"},
                {"display": "block"},
                f"Account di: {login_state.get('username')}",
                {"display": "none"}  # Hide H6 when logged in
            )
        return (
            {"display": "block"},
            {"display": "none"},
            "",
            {"display": "block", "color": "#6c757d"}  # Show H6 when not logged in
        )

    @app.callback(
        [Output("auth-feedback", "children"), Output("login-state", "data")],
        [Input("submit-auth", "n_clicks"), Input("logout-button", "n_clicks")],
        [
            State("toggle-auth", "active_tab"),
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

        if trigger_id == "logout-button":
            return html.Div(
                "Logout effettuato con successo",
                style={"color": "green", "font-weight": "500"}
            ), None

        if trigger_id == "submit-auth":
            if not username or not password:
                return html.Div(
                    "Per favore, compila tutti i campi",
                    style={"color": "#dc3545", "font-weight": "500"}
                ), None

            if tipo_auth == "login":
                stato_login, logged = firebase_auth.login(username, password)
                if logged:
                    return html.Div(
                        stato_login,
                        style={"color": "#198754", "font-weight": "500"}
                    ), {"logged_in": True, "username": username}
                else:
                    return html.Div(
                        stato_login,
                        style={"color": "#dc3545", "font-weight": "500"}
                    ), None

            elif tipo_auth == "register":
                if not gdpr_accettato:
                    return html.Div(
                        "Devi accettare i termini GDPR per registrarti",
                        style={"color": "#dc3545", "font-weight": "500"}
                    ), None
                else:
                    stato_registrazione, registered = firebase_auth.register(username, password)
                    if registered:
                        return html.Div(
                            stato_registrazione,
                            style={"color": "#198754", "font-weight": "500"}
                        ), {"logged_in": True, "username": username}
                    else:
                        return html.Div(
                            stato_registrazione,
                            style={"color": "#dc3545", "font-weight": "500"}
                        ), None

        return "", current_login_state

    return modal