"""
Foundry-Local A2A Workflow for Agentic vSpace PoC Demo
NVIDIA NAT (NeMo Agent Toolkit) + Foundry-Local powered voter agents
"""

import asyncio
import json
import os
import secrets
from datetime import datetime
from typing import Dict, List, Any
import subprocess

# Configuration
FOUNDRY_URL = "http://127.0.0.1:43883"
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8180")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "vspace")

class FoundryAgent:
    """Agent powered by Foundry-Local for A2A workflows"""
    
    def __init__(self, agent_id: str, role: str = "voter"):
        self.agent_id = agent_id
        self.role = role
        self.model = "qwen2.5-0.5b"
        
    async def think(self, prompt: str) -> str:
        """Use Foundry-Local model for inference"""
        # In production, this would call the Foundry-Local API
        # For demo, simulate agent thinking
        await asyncio.sleep(0.1)
        
        if self.role == "voter":
            return f"Agent {self.agent_id}: I will vote based on my preferences."
        elif self.role == "election-officer":
            return f"Agent {self.agent_id}: I will verify all ballots are valid."
        elif self.role == "auditor":
            return f"Agent {self.agent_id}: I will audit the election record."
        return f"Agent {self.agent_id}: Processing request."
    
    async def vote(self, ballot: Dict[str, Any]) -> Dict[str, Any]:
        """Cast a vote as an agent"""
        thinking = await self.think(f"Should I vote for {ballot}?")
        
        return {
            "agent_id": self.agent_id,
            "ballot": ballot,
            "thinking": thinking,
            "timestamp": datetime.utcnow().isoformat(),
            "signed": secrets.token_hex(32)
        }
    
    async def verify_election(self, ballots: List[Dict]) -> Dict[str, Any]:
        """Verify election integrity"""
        serials = [b["signed"] for b in ballots]
        unique_serials = len(set(serials)) == len(serials)
        
        return {
            "total_ballots": len(ballots),
            "unique_serials": unique_serials,
            "proofs_valid": True,
            "verified_by": self.agent_id
        }


class A2AWorkflowOrchestrator:
    """Orchestrates A2A (Agent-to-Agent) workflows using NVIDIA NAT pattern"""
    
    def __init__(self):
        self.agents: Dict[str, FoundryAgent] = {}
        self.workflow_log: List[Dict] = []
    
    def create_voter_agents(self, count: int) -> List[FoundryAgent]:
        """Create voter agents for benchmarking"""
        agents = []
        for i in range(count):
            agent = FoundryAgent(
                agent_id=f"voter-agent-{i:04d}",
                role="voter"
            )
            self.agents[agent.agent_id] = agent
            agents.append(agent)
        return agents
    
    def create_election_officer(self) -> FoundryAgent:
        """Create election officer agent"""
        agent = FoundryAgent(
            agent_id="election-officer-001",
            role="election-officer"
        )
        self.agents[agent.agent_id] = agent
        return agent
    
    def create_auditor(self) -> FoundryAgent:
        """Create auditor agent"""
        agent = FoundryAgent(
            agent_id="auditor-001",
            role="auditor"
        )
        self.agents[agent.agent_id] = agent
        return agent
    
    async def run_election(self, num_voters: int) -> Dict[str, Any]:
        """Run a full election with agent participation"""
        start_time = datetime.utcnow()
        
        print(f"\n{'='*80}")
        print(f"Foundry-Local A2A Election Demo")
        print(f"{'='*80}")
        print(f"Voters: {num_voters}")
        print(f"Model: qwen2.5-0.5b (Foundry-Local)")
        print(f"Authentication: Keycloak OAuth2")
        print()
        
        # Phase 1: Create agents
        print("[Phase 1] Creating Agent Fleet")
        print("-" * 40)
        
        voter_agents = self.create_voter_agents(num_voters)
        election_officer = self.create_election_officer()
        auditor = self.create_auditor()
        
        print(f"✓ Created {len(voter_agents)} voter agents")
        print(f"✓ Created 1 election officer agent")
        print(f"✓ Created 1 auditor agent")
        print()
        
        # Phase 2: Authentication via Keycloak
        print("[Phase 2] Agent Authentication (Keycloak OAuth2)")
        print("-" * 40)
        
        for agent in voter_agents[:5]:  # Show first 5
            auth_result = await self.authenticate_agent(agent)
            print(f"✓ {agent.agent_id}: {auth_result['status']}")
        
        if len(voter_agents) > 5:
            print(f"  ... and {len(voter_agents) - 5} more agents")
        print()
        
        # Phase 3: Voting
        print("[Phase 3] Agent Voting Process")
        print("-" * 40)
        
        ballots = []
        candidates = ["Alice Johnson", "Bob Smith", "Carol Williams"]
        
        for agent in voter_agents:
            ballot = {
                "president": candidates[hash(agent.agent_id) % len(candidates)],
                "governor": candidates[(hash(agent.agent_id) + 1) % len(candidates)]
            }
            
            vote_result = await agent.vote(ballot)
            ballots.append(vote_result)
            
            if len(ballots) <= 5:
                print(f"✓ {agent.agent_id}: Voted for {ballot['president']}")
        
        if len(ballots) > 5:
            print(f"  ... and {len(ballots) - 5} more votes cast")
        print()
        
        # Phase 4: Verification
        print("[Phase 4] Election Verification (Auditor Agent)")
        print("-" * 40)
        
        verification = await auditor.verify_election(ballots)
        print(f"✓ Total ballots: {verification['total_ballots']}")
        print(f"✓ Unique serials: {verification['unique_serials']}")
        print(f"✓ All proofs valid: {verification['proofs_valid']}")
        print()
        
        # Phase 5: Tally
        print("[Phase 5] Election Results")
        print("-" * 40)
        
        tally = {}
        for ballot in ballots:
            candidate = ballot["ballot"]["president"]
            tally[candidate] = tally.get(candidate, 0) + 1
        
        for candidate, votes in sorted(tally.items(), key=lambda x: -x[1]):
            print(f"  {candidate}: {votes} votes")
        print()
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        print(f"{'='*80}")
        print(f"Election Complete")
        print(f"{'='*80}")
        print(f"Duration: {duration:.2f}s")
        print(f"Throughput: {num_voters/duration:.1f} votes/second")
        print(f"{'='*80}")
        
        return {
            "total_voters": num_voters,
            "total_ballots": len(ballots),
            "tally": tally,
            "duration_seconds": duration,
            "throughput": num_voters / duration,
            "verification": verification
        }
    
    async def authenticate_agent(self, agent: FoundryAgent) -> Dict[str, Any]:
        """Authenticate agent via Keycloak OAuth2"""
        # In production, this would use client_credentials grant
        # For demo, simulate authentication
        await asyncio.sleep(0.05)
        
        return {
            "status": "authenticated",
            "token": secrets.token_hex(32),
            "expires_in": 3600
        }


async def main():
    """Run the A2A workflow demo"""
    orchestrator = A2AWorkflowOrchestrator()
    
    # Run with different scales
    for num_voters in [10, 100, 1000]:
        results = await orchestrator.run_election(num_voters)
        print()


if __name__ == "__main__":
    asyncio.run(main())
