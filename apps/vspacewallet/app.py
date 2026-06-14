"""
vSpaceWallet.com Credential Wallet PWA (F-106)
FastHTML Progressive Web Application for credential management
"""

import os
import secrets
from datetime import datetime
from typing import Dict, Any, List
from fasthtml.common import *

# Configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8180")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "vspace")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID_WALLET", "vspacewallet")

# Session store
sessions: Dict[str, Dict] = {}
credentials: Dict[str, List[Dict]] = {}

# Create app
app, rt = fast_app(
    hdrs=(
        Link(rel="stylesheet", href="/static/style.css"),
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
        Meta(name="theme-color", content="#00d9ff"),
        Meta(name="description", content="vSpaceWallet - Secure Credential Wallet"),
        Link(rel="manifest", href="/static/manifest.json"),
    )
)

@rt("/")
def get():
    return Title("vSpaceWallet"), Main(
        H1("vSpaceWallet"),
        P("Secure Credential Wallet"),
        P("F-106: Credential Management PWA"),
        Div(
            Button("Login with Keycloak", onclick="window.location.href='/auth/keycloak'"),
            Button("Quick Demo", onclick="window.location.href='/demo'"),
            cls="auth-buttons"
        ),
        cls="container"
    )

@rt("/demo")
def get():
    session_id = secrets.token_hex(16)
    sessions[session_id] = {
        "user_id": f"demo-wallet-{secrets.token_hex(4)}",
        "authenticated": True, "demo_mode": True,
        "created": datetime.utcnow().isoformat()
    }
    credentials[session_id] = [{
        "id": f"cred-{secrets.token_hex(8)}", "type": "voter-eligibility",
        "issued": datetime.utcnow().isoformat(), "expires": "2027-01-01T00:00:00Z"
    }]
    return Redirect(f"/wallet?session={session_id}")

@rt("/auth/keycloak")
def get():
    state = secrets.token_hex(32)
    sessions[state] = {"created": datetime.utcnow().isoformat()}
    keycloak_auth_url = (
        f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
        f"?client_id={KEYCLOAK_CLIENT_ID}"
        f"&redirect_uri=http://localhost:3001/auth/callback"
        f"&response_type=code&scope=openid profile email&state={state}"
    )
    return Redirect(keycloak_auth_url)

@rt("/auth/callback")
def get(code: str = "", state: str = ""):
    if state not in sessions:
        return "Invalid state", 400
    session_id = secrets.token_hex(16)
    sessions[session_id] = {
        "user_id": f"voter-{secrets.token_hex(8)}",
        "authenticated": True, "created": datetime.utcnow().isoformat()
    }
    return Redirect(f"/wallet?session={session_id}")

@rt("/wallet")
def get(session: str = ""):
    if session not in sessions:
        return Redirect("/")
    user_creds = credentials.get(session, [])
    return Title("Your Wallet"), Main(
        H1("Credential Wallet"),
        P(f"User: {sessions[session].get('user_id', 'unknown')}"),
        Div(
            H2("Your Credentials"),
            *[
                Div(
                    H3(cred.get("type", "Unknown")),
                    P(f"ID: {cred.get('id', 'N/A')}"),
                    P(f"Issued: {cred.get('issued', 'N/A')}"),
                    P(f"Expires: {cred.get('expires', 'N/A')}"),
                    cls="credential-card"
                ) for cred in user_creds
            ] if user_creds else [P("No credentials yet")],
            cls="credentials-list"
        ),
        Div(Button("Request New Credential", onclick="window.location.href='/wallet/request'"), cls="actions"),
        cls="container"
    )

@rt("/wallet/request")
def get(session: str = ""):
    return Title("Request Credential"), Main(
        H1("Request New Credential"),
        P("F-106: Request anonymous credential via SAAC protocol"),
        Form(
            Fieldset(
                Legend("Credential Type"),
                Label(Input(type="radio", name="type", value="voter-eligibility", checked=True), " Voter Eligibility"),
                Label(Input(type="radio", name="type", value="election-officer"), " Election Officer"),
            ),
            Input(type="hidden", name="session", value=session),
            Button("Request", type="submit"),
            action="/wallet/request/submit", method="post",
        ),
        cls="container"
    )

@rt("/wallet/request/submit")
def post(type: str = "", session: str = ""):
    cred_id = f"cred-{secrets.token_hex(8)}"
    if session not in credentials:
        credentials[session] = []
    credentials[session].append({
        "id": cred_id, "type": type,
        "issued": datetime.utcnow().isoformat(), "expires": "2027-01-01T00:00:00Z"
    })
    return Redirect(f"/wallet?session={session}")

@rt("/static/manifest.json")
def get():
    return {
        "name": "vSpaceWallet", "short_name": "Wallet", "start_url": "/",
        "display": "standalone", "background_color": "#0f3460", "theme_color": "#00d9ff",
        "icons": [{"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"}]
    }

if __name__ == "__main__":
    print("F-106: vSpaceWallet.com Credential Wallet PWA")
    print("Starting server on port 3001...")
    serve(port=3001, host="0.0.0.0")
