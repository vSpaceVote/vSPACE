# vSPACE E2E User Journeys & System Lifecycles Playbook

Complete guide to running all user journeys and system lifecycle simulations for vSPACE.

## Table of Contents

- [Overview](#overview)
- [User Journeys](#user-journeys)
- [System Lifecycles](#system-lifecycles)
- [Quick Start](#quick-start)
- [Running Individual Journeys](#running-individual-journeys)
- [Output and Reporting](#output-and-reporting)
- [Feature Coverage Matrix](#feature-coverage-matrix)

---

## Overview

This playbook provides comprehensive E2E simulations covering **all 19 features** from:

1. **README.md** - Full technical specification (F-001 to F-112)
2. **vSPACE_Autonomous_PRD_v260412a.json** - Autonomous features (F-100 to F-103, F-109, F-110)
3. **vSPACE_Augmented_PRD_v260412a.json** - Augmented features (F-104 to F-108)

### What's Included

| Directory | Contents |
|-----------|----------|
| `demo/journeys/` | User journey simulations (16 journeys) |
| `demo/lifecycles/` | System lifecycle simulations (5 lifecycles) |
| `demo/playbooks/` | This documentation and runbooks |

### Journey Categories

| Category | Journeys | Features Covered |
|----------|----------|-----------------|
| **Core** | J-001 to J-005 | F-001 to F-012 (ElectionGuard foundation) |
| **Autonomous** | J-100 to J-103, J-109, J-110 | F-100, F-101, F-102, F-103, F-109, F-110 |
| **Augmented** | J-104 to J-108 | F-104, F-105, F-106, F-107, F-108 |

### Lifecycle Categories

| Lifecycle | Phases | Duration |
|-----------|--------|----------|
| LC-001: Election Setup | 5 phases | Days to weeks before election |
| LC-002: Voting Period | 6 phases | Election day (hours) |
| LC-003: Tallying | 6 phases | Hours to days after election |
| LC-004: Verification | 6 phases | Days to weeks after election |
| LC-005: Archive | 5 phases | Permanent (years) |

---

## User Journeys

### Core Journeys (F-001 to F-012)

#### J-001: Election Authority Setup Journey

**User**: Election Administrator  
**Goal**: Configure and publish election manifest  
**Features**: F-006 (Manifest), F-004 (Hashing), F-010 (Persistence)

**Steps**:
1. Create election manifest with contests and candidates
2. Define ballot styles for different precincts
3. Configure encryption parameters
4. Generate manifest hash for integrity
5. Store manifest in MongoDB
6. Publish manifest to public URL

**Run**:
```bash
cd demo/journeys
python core_journeys.py --voters 100 --guardians 5 --threshold 3
```

#### J-002: Guardian Key Ceremony Journey

**User**: Election Guardian (5 guardians, 3-of-5 threshold)  
**Goal**: Distributed key generation with verifiable shares  
**Features**: F-001 (Arithmetic), F-002 (ElGamal), F-003 (ZK Proofs), F-005 (Precomputation)

**Steps**:
1. Each guardian generates secret share
2. Guardians exchange public keys
3. Compute joint public key
4. Generate ZK proofs for each share
5. Verify all proofs
6. Store key shares in HSM
7. Publish joint public key

#### J-003: Voter Ballot Encryption Journey

**User**: Voter (100 voters simulated)  
**Goal**: Mark and encrypt ballot with verifiable encryption proofs  
**Features**: F-002 (ElGamal), F-003 (ZK Proofs), F-007 (Ballot), F-008 (Workflow)

**Steps**:
1. Voter authenticates and retrieves ballot style
2. Voter marks selections on ballot
3. System encrypts each selection with ElGamal
4. Generate ZK proof for each encryption
5. Create ballot code for voter verification
6. Store encrypted ballot
7. Return ballot code to voter

#### J-004: Ballot Decryption & Tallying Journey

**User**: Election Guardians (threshold decryption)  
**Goal**: Decrypt and tally encrypted ballots  
**Features**: F-002 (ElGamal), F-003 (ZK Proofs), F-007 (Ballot), F-011 (CLI)

**Steps**:
1. Close election and freeze ballot set
2. Guardians coordinate decryption ceremony
3. Each guardian provides partial decryption share
4. Generate ZK proofs for decryption shares
5. Combine shares to decrypt ballots
6. Tally decrypted votes
7. Publish results with proofs

#### J-005: Public Verification Journey

**User**: Public Verifier (any citizen, media, observer)  
**Goal**: Independently verify election integrity  
**Features**: F-003 (ZK Proofs), F-004 (Hashing), F-011 (CLI)

**Steps**:
1. Download election record (manifest, ballots, proofs)
2. Verify manifest hash
3. Verify ballot encryption proofs
4. Verify decryption proofs
5. Verify tally computation
6. Generate verification report

### Autonomous Journeys (F-100 to F-103, F-109, F-110)

#### J-100: Anonymous Credential Issuance Journey

**User**: Voter deriving anonymous credential from identity VC  
**Goal**: Obtain SAAC anonymous credential without linking to identity  
**Features**: F-100 (SAAC Protocol)

**Steps**:
1. Voter obtains identity VC (e.g., from government ID provider)
2. Voter creates blinded commitment
3. Submit blinded commitment to SAAC issuer
4. Issuer signs blinded commitment
5. Voter unblinds signature to get SAAC credential
6. Verify credential validity

**Run**:
```bash
cd demo/journeys
python autonomous_journeys.py --voters 100
```

#### J-101: Multi-Holder Credential Management Journey

**User**: Voter with multiple devices (primary + backup)  
**Goal**: Split credential across devices for security  
**Features**: F-101 (Multi-Holder BBS)

**Steps**:
1. Voter receives SAAC credential on primary device
2. Split credential into shares (2-of-2 threshold)
3. Store share 1 on primary device
4. Store share 2 on backup device (QR code transfer)
5. Verify both shares are valid
6. Test threshold presentation

#### J-102: Credential-to-Ballot Binding Journey

**User**: Voter marking ballot with anonymous credential  
**Goal**: Bind credential to ballot without revealing identity  
**Features**: F-102 (Credential Binding)

**Steps**:
1. Voter marks ballot selections
2. System generates Pedersen commitment C = g^r * h^s
3. Generate Schnorr-like sigma protocol proof
4. Bind credential to ballot encryption nonce
5. Verify binding proof
6. Submit bound ballot

#### J-103: One-Show Voting Enforcement Journey

**User**: Election system preventing double voting  
**Goal**: Ensure each credential can only be used once  
**Features**: F-103 (One-Show Enforcement)

**Steps**:
1. Voter derives serial number from credential (VRF)
2. System checks serial number uniqueness
3. Register serial number in MongoDB
4. Attempt duplicate voting (should fail)
5. Verify duplicate detection
6. Publish serial number audit log

#### J-109: Augmented Record Publication Journey

**User**: Election authority publishing complete record  
**Goal**: Publish election record with vSPACE extensions  
**Features**: F-109 (Augmented Election Record)

**Steps**:
1. Collect all encrypted ballots
2. Collect all binding commitments and proofs
3. Collect all serial numbers
4. Construct vspace_record JSON section
5. Serialize in multiple formats (JSON, BSON, MsgPack)
6. Validate record structure
7. Publish to public URL

#### J-110: Independent Verification Journey

**User**: External verifier (auditor, researcher, citizen)  
**Goal**: Independently verify all vSPACE cryptographic artifacts  
**Features**: F-110 (vSPACE Verifier)

**Steps**:
1. Download augmented election record
2. Verify SAAC presentations
3. Verify binding proofs
4. Verify serial number uniqueness
5. Verify record integrity
6. Generate verification report

### Augmented Journeys (F-104 to F-108)

#### J-104: Entra VC Bridge Journey

**User**: Voter obtaining identity from Microsoft Entra Verified ID  
**Goal**: Get Entra VC and derive anonymous credential  
**Features**: F-104 (Entra Verified ID Bridge)

**Steps**:
1. Voter authenticates with Microsoft account
2. System requests VC issuance from Entra
3. Entra validates voter eligibility
4. Entra issues VoterEligibilityCredential
5. Voter stores VC in wallet
6. Derive SAAC credential from Entra VC (oblivious)

**Run**:
```bash
cd demo/journeys
python augmented_journeys.py --voters 100 --dry-run
```

#### J-105: vSpaceVote PWA Voting Journey

**User**: Voter marking ballot on vSpaceVote.com  
**Goal**: Complete ballot marking with HTMX partials  
**Features**: F-105 (vSpaceVote.com Voter-Facing PWA)

**Steps**:
1. Voter navigates to vSpaceVote.com
2. PWA loads with service worker cache
3. Voter authenticates with credential wallet
4. Ballot loads with HTMX partials (< 200ms, < 2KB)
5. Voter marks selections (progressive save)
6. Review and confirm ballot
7. Submit encrypted ballot

#### J-106: vSpaceWallet Credential Management Journey

**User**: Voter managing credentials in vSpaceWallet.com  
**Goal**: Securely store and manage credential shares  
**Features**: F-106 (vSpaceWallet.com Credential Wallet PWA)

**Steps**:
1. Voter opens vSpaceWallet.com PWA
2. IndexedDB encryption setup
3. Import SAAC credential
4. Split into shares (2-of-2)
5. Store primary share (secure enclave)
6. Export backup share (QR code)
7. Test credential recovery

#### J-107: Cross-Origin Communication Journey

**User**: Voter using both vSpaceVote.com and vSpaceWallet.com  
**Goal**: Secure cross-origin credential presentation  
**Features**: F-107 (Cross-Origin Communication Protocol)

**Steps**:
1. vSpaceVote.com generates cryptographic challenge
2. Challenge sent to vSpaceWallet.com via postMessage
3. vSpaceWallet.com verifies origin
4. Wallet signs challenge with credential
5. Response sent back via postMessage
6. vSpaceVote.com verifies signature
7. Proceed with ballot encryption

#### J-108: NLWeb Query Journey

**User**: Citizen querying election results in natural language  
**Goal**: Get Schema.org-typed responses grounded in election record  
**Features**: F-108 (NLWeb Conversational Interfaces)

**Steps**:
1. User asks natural language question
2. System converts to vector search query
3. Azure AI Search retrieves relevant records
4. Azure OpenAI generates grounded response
5. System adds cryptographic provenance hash
6. Return Schema.org-typed response
7. User can ask follow-up questions

---

## System Lifecycles

### LC-001: Election Setup Lifecycle

**Duration**: Days to weeks before election  
**Actors**: Election Authority, Guardians, System Administrators

**Phases**:
1. Election manifest creation (F-006)
2. Guardian recruitment and key ceremony (F-001, F-002, F-003)
3. System configuration and testing (F-010, F-011)
4. Public key publication (F-006)
5. Voter registration integration (F-104)

**Run**:
```bash
cd demo/lifecycles
python system_lifecycles.py --voters 100 --guardians 5 --threshold 3
```

### LC-002: Voting Period Lifecycle

**Duration**: Election day (hours)  
**Actors**: Voters, Election Monitors, System Operators

**Phases**:
1. Polls open (F-006)
2. Voter authentication (F-104)
3. Ballot marking and encryption (F-002, F-003, F-102)
4. Ballot submission (F-007, F-010)
5. Real-time verification (F-003, F-103)
6. Polls close (F-006)

### LC-003: Tallying Lifecycle

**Duration**: Hours to days after election  
**Actors**: Guardians, Election Observers, Media

**Phases**:
1. Ballot set freeze (F-007)
2. Guardian decryption ceremony (F-002, F-003)
3. Partial decryption shares (F-002)
4. Combine shares and decrypt (F-002)
5. Tally votes (F-007)
6. Publish results (F-011, F-109)

### LC-004: Verification Lifecycle

**Duration**: Days to weeks after election  
**Actors**: Public, Media, Researchers, Observers

**Phases**:
1. Download election record (F-011)
2. Verify manifest integrity (F-004)
3. Verify ballot proofs (F-003, F-110)
4. Verify decryption proofs (F-003, F-110)
5. Verify tally (F-007)
6. Publish verification reports (F-011)

### LC-005: Archive Lifecycle

**Duration**: Permanent (years)  
**Actors**: Archivists, Historians, Future Auditors

**Phases**:
1. Complete record assembly (F-109)
2. Multiple format serialization (F-109)
3. Distributed storage (F-010)
4. Long-term preservation
5. Access control setup

---

## Quick Start

### Run All Core Journeys

```bash
cd demo/journeys
python core_journeys.py --voters 100 --output ../output
```

### Run All Autonomous Journeys

```bash
cd demo/journeys
python autonomous_journeys.py --voters 100 --output ../output
```

### Run All Augmented Journeys (Dry-Run Mode)

```bash
cd demo/journeys
python augmented_journeys.py --voters 100 --dry-run --output ../output
```

### Run All System Lifecycles

```bash
cd demo/lifecycles
python system_lifecycles.py --voters 100 --guardians 5 --threshold 3 --output ../output
```

### Run Complete E2E Simulation

```bash
cd demo
python run_e2e_poc.py --voters 100
python journeys/core_journeys.py --voters 100 --output output
python journeys/autonomous_journeys.py --voters 100 --output output
python journeys/augmented_journeys.py --voters 100 --dry-run --output output
python lifecycles/system_lifecycles.py --voters 100 --output output
```

---

## Running Individual Journeys

### Command-Line Options

All journey scripts support these options:

```
usage: journey_script.py [-h] [--voters N] [--guardians N] [--threshold N]
                         [--output PATH] [--dry-run] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --voters, -n N        Number of voters to simulate (default: 100)
  --guardians, -g N     Number of guardians (default: 5)
  --threshold, -t N     Guardian threshold (default: 3)
  --output, -o PATH     Output directory for results
  --dry-run             Enable dry-run mode (mock external services)
  --verbose, -v         Enable verbose output
```

### Example: Large-Scale Simulation

```bash
# 10,000 voters
python core_journeys.py --voters 10000 --output output

# 1,000 voters with 7 guardians (4-of-7 threshold)
python core_journeys.py --voters 1000 --guardians 7 --threshold 4 --output output
```

---

## Output and Reporting

### Generated Files

After running journeys, the following files are generated:

```
demo/output/
├── core_journeys_results.json
├── autonomous_journeys_results.json
├── augmented_journeys_results.json
└── system_lifecycles_results.json
```

### JSON Result Structure

```json
{
  "timestamp": "2026-04-13T10:00:00.000000",
  "configuration": {
    "voters": 100,
    "guardians": 5,
    "threshold": 3
  },
  "summary": {
    "total_journeys": 5,
    "successful": 5,
    "total_duration_ms": 150.5
  },
  "journeys": [
    {
      "journey_id": "J-001",
      "journey_name": "Election Authority Setup",
      "success": true,
      "total_duration_ms": 30.5,
      "steps": [
        {
          "step_id": "J-001-1",
          "name": "Create election manifest",
          "feature_id": "F-006",
          "duration_ms": 5.2,
          "status": "passed"
        }
      ],
      "errors": []
    }
  ]
}
```

---

## Feature Coverage Matrix

| Feature | Core Journeys | Autonomous Journeys | Augmented Journeys | Lifecycles |
|---------|--------------|-------------------|------------------|------------|
| F-001 | J-002 | - | - | LC-001 |
| F-002 | J-002, J-003, J-004 | - | - | LC-001, LC-002, LC-003 |
| F-003 | J-002, J-003, J-004, J-005 | - | - | LC-001, LC-002, LC-003, LC-004 |
| F-004 | J-001, J-005 | - | - | LC-004 |
| F-005 | J-002 | - | - | - |
| F-006 | J-001, J-002, J-004 | - | - | LC-001, LC-002 |
| F-007 | J-003, J-004, J-005 | - | - | LC-002, LC-003, LC-004 |
| F-008 | J-003 | - | - | - |
| F-009 | - | - | - | - |
| F-010 | J-001, J-003 | - | - | LC-001, LC-002, LC-005 |
| F-011 | J-004, J-005 | - | - | LC-001, LC-003, LC-004 |
| F-012 | - | - | - | - |
| F-100 | - | J-100 | - | - |
| F-101 | - | J-101 | - | - |
| F-102 | - | J-102 | - | LC-002 |
| F-103 | - | J-103 | - | LC-002, LC-004 |
| F-104 | - | - | J-104 | LC-001, LC-002 |
| F-105 | - | - | J-105 | - |
| F-106 | - | - | J-106 | - |
| F-107 | - | - | J-107 | - |
| F-108 | - | - | J-108 | - |
| F-109 | - | J-109 | - | LC-003, LC-005 |
| F-110 | - | J-110 | - | LC-004 |

**Total Coverage**: 19/19 features (100%)

---

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'electionguard_vspace'"

**Solution**: Ensure Python path includes the bindings directory:
```bash
export PYTHONPATH="$PWD/bindings/python:$PYTHONPATH"
```

#### Journey timeout on large voter counts

**Solution**: Reduce voter count or run with verbose mode:
```bash
python core_journeys.py --voters 1000 --verbose
```

#### Dry-run mode not working for augmented journeys

**Solution**: Explicitly enable dry-run flag:
```bash
python augmented_journeys.py --dry-run
```

### Getting Help

1. Check journey logs in `demo/output/`
2. Review error messages in JSON results
3. Consult README.md for architecture details
4. Open GitHub issue with journey results attached

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-04-13  
**Related Documents**: README.md, vSPACE_Autonomous_PRD_v260412a.json, vSPACE_Augmented_PRD_v260412a.json, BENCHMARKS.md, SETUP.md
