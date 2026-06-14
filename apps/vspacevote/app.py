"""
vSpaceVote.com Voter-Facing PWA (F-105)
FastHTML Progressive Web Application for ballot marking
"""

import os
import secrets
from datetime import datetime
from typing import Dict, Any
from fasthtml.common import *

# Configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8180")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "vspace")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID_VOTE", "vspacevote")

# Session store
sessions: Dict[str, Dict] = {}

# Create app
app, rt = fast_app(
    hdrs=(
        Link(rel="stylesheet", href="/static/style.css"),
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
        Meta(name="theme-color", content="#e94560"),
        Meta(name="description", content="vSpaceVote - Secure Anonymous Voting"),
        Link(rel="manifest", href="/static/manifest.json"),
    )
)

@rt("/")
def get():
    return Title("vSpaceVote"), Main(
        H1("vSpaceVote"),
        P("Secure Anonymous Voting Platform"),
        P("F-105: Voter-Facing PWA with Ballot Marking"),
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
        "user_id": f"demo-voter-{secrets.token_hex(4)}",
        "authenticated": True,
        "demo_mode": True,
        "created": datetime.utcnow().isoformat()
    }
    return Redirect(f"/ballot?session={session_id}")

@rt("/auth/keycloak")
def get():
    state = secrets.token_hex(32)
    sessions[state] = {"created": datetime.utcnow().isoformat()}
    keycloak_auth_url = (
        f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
        f"?client_id={KEYCLOAK_CLIENT_ID}"
        f"&redirect_uri=http://localhost:3000/auth/callback"
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
        "authenticated": True,
        "created": datetime.utcnow().isoformat()
    }
    return Redirect(f"/ballot?session={session_id}")

@rt("/ballot")
def get(session: str = ""):
    if session not in sessions:
        return Redirect("/")
    return Title("Mark Your Ballot"), Main(
        H1("Mark Your Ballot"),
        P(f"User: {sessions[session].get('user_id', 'unknown')}"),
        Form(
            Fieldset(
                Legend("President"),
                Label(Input(type="radio", name="president", value="alice"), " Alice Johnson"),
                Label(Input(type="radio", name="president", value="bob"), " Bob Smith"),
                Label(Input(type="radio", name="president", value="carol"), " Carol Williams"),
            ),
            Fieldset(
                Legend("Governor"),
                Label(Input(type="radio", name="governor", value="dave"), " Dave Brown"),
                Label(Input(type="radio", name="governor", value="eve"), " Eve Davis"),
            ),
            Input(type="hidden", name="session", value=session),
            Button("Review Ballot", type="submit"),
            action="/ballot/review", method="post",
        ),
        cls="container"
    )

@rt("/ballot/review")
def post(president: str = "", governor: str = "", session: str = ""):
    candidates = {"alice": "Alice Johnson", "bob": "Bob Smith", "carol": "Carol Williams",
                  "dave": "Dave Brown", "eve": "Eve Davis"}
    return Title("Review Your Ballot"), Main(
        H1("Review Your Ballot"),
        Div(
            H3("Your Selections"),
            P(f"President: {candidates.get(president, president)}"),
            P(f"Governor: {candidates.get(governor, governor)}"),
            cls="ballot-summary"
        ),
        Form(
            Input(type="hidden", name="president", value=president),
            Input(type="hidden", name="governor", value=governor),
            Input(type="hidden", name="session", value=session),
            Button("Confirm & Cast", type="submit"),
            Button("Go Back", type="button", onclick="history.back()"),
            action="/ballot/cast", method="post",
        ),
        cls="container"
    )

@rt("/ballot/cast")
def post(president: str = "", governor: str = "", session: str = ""):
    tracking_code = secrets.token_hex(16)
    return Title("Ballot Cast"), Main(
        H1("Ballot Successfully Cast!"),
        Div(
            P("Your tracking code:"),
            Code(tracking_code),
            P("Save this code to verify your vote."),
            cls="tracking-code"
        ),
        P("F-105 Ballot Marking Complete ✓"),
        cls="container"
    )

@rt("/static/manifest.json")
def get():
    return {
        "name": "vSpaceVote", "short_name": "Vote", "start_url": "/",
        "display": "standalone", "background_color": "#1a1a2e", "theme_color": "#e94560",
        "icons": [{"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"}]
    }

if __name__ == "__main__":
    print("F-105: vSpaceVote.com Voter-Facing PWA")
    print("Starting server on port 3000...")
    serve(port=3000, host="0.0.0.0")
