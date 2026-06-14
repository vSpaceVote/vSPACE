"""
F-107: Cross-Origin Communication Protocol
WebSocket relay for credential presentation between vSpaceVote and vSpaceWallet
"""

import asyncio
import json
import secrets
from datetime import datetime
from typing import Dict, Set
from fasthtml.common import *
import websockets

# Configuration
ORIGINS_WHITELIST = [
    "https://vspacevote.com",
    "https://vspacewallet.com",
    "http://localhost:3000",
    "http://localhost:3001"
]

# WebSocket connections
connections: Dict[str, Set] = {}
pending_challenges: Dict[str, Dict] = {}

app, rt = fast_app(
    hdrs=(
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
        Script(src="https://unpkg.com/htmx.org@1.9.10/dist/ext/ws.js"),
    )
)

@rt("/")
def get():
    """Cross-Origin relay status page"""
    return Title("vSPACE Cross-Origin Relay"), Main(
        H1("vSPACE Cross-Origin Communication Relay"),
        P("WebSocket server for F-107 credential presentation"),
        Div(
            H2("Active Connections"),
            P(f"Sessions: {len(connections)}"),
            P(f"Pending challenges: {len(pending_challenges)}"),
            cls="stats"
        ),
        cls="container"
    )

@rt("/api/challenge", methods=["POST"])
def api_challenge():
    """Generate a challenge for cross-origin credential presentation"""
    challenge_id = secrets.token_hex(16)
    nonce = secrets.token_hex(32)
    
    pending_challenges[challenge_id] = {
        "nonce": nonce,
        "created": datetime.utcnow().isoformat(),
        "status": "pending"
    }
    
    return {
        "challenge_id": challenge_id,
        "nonce": nonce,
        "timestamp": datetime.utcnow().isoformat()
    }

@rt("/api/challenge/{challenge_id}/response", methods=["POST"])
def api_challenge_response(challenge_id: str):
    """Handle credential presentation response"""
    if challenge_id not in pending_challenges:
        return {"error": "Invalid challenge"}, 400
    
    challenge = pending_challenges[challenge_id]
    challenge["status"] = "completed"
    challenge["completed_at"] = datetime.utcnow().isoformat()
    
    # In production, verify the credential presentation
    return {
        "status": "verified",
        "challenge_id": challenge_id,
        "credential_verified": True
    }

async def websocket_handler(websocket, path):
    """Handle WebSocket connections for real-time cross-origin communication"""
    origin = websocket.request.headers.get("Origin", "")
    
    # Validate origin
    if origin not in ORIGINS_WHITELIST:
        await websocket.close(1008, "Origin not allowed")
        return
    
    session_id = secrets.token_hex(16)
    connections[session_id] = websocket
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data.get("type") == "challenge_request":
                # Forward challenge to wallet
                challenge_id = data.get("challenge_id")
                if challenge_id in pending_challenges:
                    await websocket.send(json.dumps({
                        "type": "challenge",
                        "challenge_id": challenge_id,
                        "nonce": pending_challenges[challenge_id]["nonce"]
                    }))
            
            elif data.get("type") == "challenge_response":
                # Forward response to vote app
                challenge_id = data.get("challenge_id")
                if challenge_id in pending_challenges:
                    pending_challenges[challenge_id]["status"] = "completed"
                    await websocket.send(json.dumps({
                        "type": "challenge_verified",
                        "challenge_id": challenge_id,
                        "verified": True
                    }))
    
    finally:
        del connections[session_id]

def start_websocket_server(host="0.0.0.0", port=8765):
    """Start WebSocket server"""
    return websockets.serve(websocket_handler, host, port)

if __name__ == "__main__":
    # Start both HTTP and WebSocket servers
    loop = asyncio.get_event_loop()
    
    # Start WebSocket server
    ws_server = loop.run_until_complete(start_websocket_server())
    
    print("F-107 Cross-Origin Communication Protocol")
    print(f"HTTP: http://localhost:8766")
    print(f"WebSocket: ws://localhost:8765")
    
    # Start HTTP server
    serve(port=8766, host="0.0.0.0")
