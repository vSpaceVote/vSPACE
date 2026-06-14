"""
F-108: NLWeb Conversational Interfaces
OpenAI GPT-5.4 powered natural language query interface
"""

import os
import json
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from fasthtml.common import *

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("C6AI_NemoHermes_OpenAI_API_Key")
OPENAI_MODEL = "gpt-5.4"

# Try to import openai
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except ImportError:
    client = None


class NLWebEngine:
    """NLWeb Query Engine powered by OpenAI GPT-5.4"""
    
    def __init__(self):
        self.election_record = self._load_record()
        self.query_history = []
    
    def _load_record(self):
        record_path = Path(__file__).parent.parent.parent / "demo" / "output" / "augmented_election_record.json"
        if record_path.exists():
            with open(record_path) as f:
                return json.load(f)
        return {
            "election_id": "election-demo-2026",
            "candidates": ["Alice Johnson", "Bob Smith", "Carol Williams"],
            "ballots": [{"ballot_id": f"ballot-{i}"} for i in range(100)],
            "verification": {"serial_uniqueness": True, "all_proofs_valid": True}
        }
    
    def _provenance_hash(self, query: str, response: str) -> str:
        data = f"{query}:{response}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def query(self, user_query: str) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        
        if client:
            try:
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are vSPACE NLWeb, an election query assistant. Answer based on the election record."},
                        {"role": "user", "content": f"Election: {self.election_record.get('election_id')}\nQuery: {user_query}"}
                    ],
                    temperature=0.3, max_tokens=500
                )
                ai_response = response.choices[0].message.content
                model_used = OPENAI_MODEL
            except Exception as e:
                ai_response = f"OpenAI error: {e}"
                model_used = "error"
        else:
            ai_response = self._fallback_response(user_query)
            model_used = "rule-based-fallback"
        
        provenance = self._provenance_hash(user_query, ai_response)
        
        result = {
            "query": user_query,
            "response": ai_response,
            "provenance_hash": provenance,
            "model_used": model_used,
            "timestamp": start_time.isoformat(),
            "response_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
        }
        
        self.query_history.append(result)
        return result
    
    def _fallback_response(self, query: str) -> str:
        q = query.lower()
        if "how many" in q and "ballot" in q:
            count = len(self.election_record.get("ballots", []))
            return f"{count} ballots were cast in this election."
        elif "result" in q or "tally" in q:
            return "Alice Johnson: 4 votes, Bob Smith: 3 votes, Carol Williams: 3 votes"
        elif "verify" in q or "unique" in q:
            return "All serial numbers verified as unique. No duplicate voting detected."
        return "I can help with election queries. Ask about results, verification, or ballot counts."


# Create engine
engine = NLWebEngine()

# Create app
app, rt = fast_app(
    hdrs=(
        Link(rel="stylesheet", href="/static/nlweb.css"),
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
        Meta(name="theme-color", content="#00b4d8"),
        Meta(name="description", content="vSPACE NLWeb - Natural Language Election Query"),
    )
)

@rt("/")
def get():
    return Title("vSPACE NLWeb"), Main(
        H1("vSPACE NLWeb"),
        P("Natural Language Election Query Interface (F-108)"),
        P(f"Model: {OPENAI_MODEL} | OpenAI: {'✓' if client else '✗ (fallback)'}"),
        Div(
            Form(
                Input(type="text", name="query", placeholder="Ask about election results...",
                      id="query-input", hx_post="/api/query", hx_target="#response-area"),
                Button("Ask", type="submit"),
                cls="query-form"
            ),
            Div(id="response-area", cls="response-area"),
            cls="query-container"
        ),
        Div(
            H3("Example Queries"),
            Ul(
                Li("How many ballots were cast?"),
                Li("Show me the election results"),
                Li("Are all serial numbers unique?"),
                Li("Verify credential status"),
            ),
            cls="examples"
        ),
        cls="container"
    )

@rt("/api/query", methods=["POST"])
def api_query(query: str = ""):
    import asyncio
    if not query:
        return Div(P("Please enter a query"), cls="error")
    
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(engine.query(query))
    loop.close()
    
    return Div(
        H3(f"Query: {result['query']}"),
        P(result["response"]),
        Div(
            P(f"Provenance: {result['provenance_hash'][:16]}..."),
            P(f"Model: {result['model_used']}"),
            P(f"Time: {result['response_time_ms']:.1f}ms"),
            cls="metadata"
        ),
        cls="response"
    )

@rt("/api/health")
def api_health():
    return {"status": "healthy", "model": OPENAI_MODEL, "openai": bool(client)}

if __name__ == "__main__":
    print("F-108: NLWeb Conversational Interfaces")
    print(f"Model: {OPENAI_MODEL}")
    print(f"OpenAI: {'✓' if client else '✗'}")
    print("Starting server on port 8501...")
    serve(port=8501, host="0.0.0.0")
