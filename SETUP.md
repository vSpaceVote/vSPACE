# vSPACE Setup and Staging Guide

This guide provides complete instructions for setting up vSPACE Augmented PRD features (F-104 through F-108) in both development and production environments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start (Dry-Run Mode)](#quick-start-dry-run-mode)
- [Production Staging](#production-staging)
  - [Step 1: Microsoft Entra Verified ID Setup](#step-1-microsoft-entra-verified-id-setup)
  - [Step 2: Azure OpenAI Service Setup](#step-2-azure-openai-service-setup)
  - [Step 3: Azure AI Search Setup](#step-3-azure-ai-search-setup)
  - [Step 4: Azure Cosmos DB Setup](#step-4-azure-cosmos-db-setup)
  - [Step 5: Azure App Service Setup](#step-5-azure-app-service-setup)
- [Configuration Wizard](#configuration-wizard)
- [Validation](#validation)
- [Running the E2E PoC Demo](#running-the-e2e-poc-demo)
- [Troubleshooting](#troubleshooting)

---

## Overview

The vSPACE Augmented PRD extends ElectionGuard with the following features:

| Feature | Description | Azure Services |
|---------|-------------|----------------|
| **F-104** | Entra Verified ID Bridge | Azure AD, Entra Verified ID |
| **F-105** | vSpaceVote.com PWA | Azure App Service, Front Door |
| **F-106** | vSpaceWallet.com PWA | Azure App Service |
| **F-107** | Cross-Origin Communication | WebSocket relay |
| **F-108** | NLWeb Conversational Interfaces | Azure OpenAI, AI Search |
| **F-010** | MongoDB Persistence | Azure Cosmos DB (MongoDB API) |
| **F-103** | One-Show Enforcement | Cosmos DB serial numbers collection |
| **F-109** | Augmented Election Record | Cosmos DB, Key Vault |

**Deployment Modes:**

- **Dry-Run Mode**: All Azure API calls are mocked. Safe for local development and testing.
- **Production Mode**: Live Azure service integration. Requires valid credentials and subscriptions.

---

## Prerequisites

### Required Software

- Python 3.9+
- Git
- Azure CLI (for production deployment)
- Azure subscription with access to:
  - Azure AD Premium P2 or Microsoft Entra Suite
  - Azure OpenAI Service
  - Azure AI Search
  - Azure Cosmos DB
  - Azure App Service

### Azure Permissions

You need the following Azure AD permissions:

- **VerifiableCredential.Create.All** (for Entra Verified ID)
- **Admin Consent** granted for the application
- **Subscription Contributor** or **Owner** role for resource provisioning

---

## Quick Start (Dry-Run Mode)

For initial setup and testing without Azure credentials:

```bash
# Navigate to setup directory
cd setup

# Run the interactive wizard
python wizard.py

# When prompted, accept defaults and enable dry-run mode

# Validate configuration
python validate.py

# Run the E2E PoC demo
cd ../demo
python run_e2e_poc.py --voters 10
```

**Expected Output:**

```
================================================================================
vSPACE Dry-Run E2E PoC Demo
================================================================================
Configuration: 10 voters
Output directory: ./output

[Phase 1] Election Setup
----------------------------------------
✓ Election manifest generated: election-abc123
✓ SAAC parameters generated

[Phase 2] Voter Registration & Credential Issuance (F-104)
----------------------------------------
✓ Voter voter-001: Entra VC → SAAC credential derived
...

[Phase 7] Verification Summary
----------------------------------------
✓ serial_uniqueness: PASS
✓ binding_proofs_valid: PASS
✓ saac_params_consistent: PASS
✓ record_structure_valid: PASS

================================================================================
Demo Complete
================================================================================
Total voters: 10
Ballots cast: 10
Errors: 0
```

---

## Production Staging

### Step 1: Microsoft Entra Verified ID Setup (F-104)

#### 1.1 Create Azure AD Application

```bash
# Login to Azure
az login

# Create Azure AD application
az ad app create \
  --display-name "vSPACE Verified ID" \
  --sign-in-audience AzureADMultipleOrgs
```

**Note the output:**
- `appId` → `AZURE_AD_APP_CLIENT_ID`
- `id` → Object ID (for later steps)

#### 1.2 Create Client Secret

```bash
az ad app credential reset \
  --id <APP_OBJECT_ID> \
  --append
```

**Save the generated password** → `AZURE_AD_APP_CLIENT_SECRET`

#### 1.3 Grant API Permissions

1. Navigate to **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Select your vSPACE application
3. Go to **API permissions** → **Add a permission**
4. Select **Microsoft APIs** → **Microsoft Graph**
5. Add **Application permission**: `VerifiableCredential.Create.All`
6. Click **Grant admin consent**

#### 1.4 Configure Entra Verified ID Service

1. Go to **Azure Portal** → **Entra Verified ID**
2. Create a new **Verified ID service**
3. Note the **Tenant ID** → `AZURE_ENTRA_TENANT_ID`

#### 1.5 Create VoterEligibilityCredential Contract

1. In Entra Verified ID portal, go to **Credential rules**
2. Create new contract with:
   - **Name**: `VoterEligibilityCredential`
   - **Claims**:
     - `election_id` (string)
     - `precinct` (string)
     - `blinded_commitment` (string)
3. Configure **Issuance callback URL**: `https://vspacewallet.com/api/v1/vspace/entra/callback`

#### 1.6 Register DID Document

Create `did.json` and host at `https://vspacevote.com/.well-known/did.json`:

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1"
  ],
  "id": "did:web:vspacevote.com",
  "verificationMethod": [{
    "id": "did:web:vspacevote.com#keys-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:web:vspacevote.com",
    "publicKeyMultibase": "<YOUR_PUBLIC_KEY>"
  }],
  "authentication": ["did:web:vspacevote.com#keys-1"],
  "assertionMethod": ["did:web:vspacevote.com#keys-1"]
}
```

---

### Step 2: Azure OpenAI Service Setup (F-108)

#### 2.1 Create Azure OpenAI Resource

```bash
az cognitiveservices account create \
  --name <your-openai-resource> \
  --resource-group <your-resource-group> \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

#### 2.2 Deploy Model

1. Go to **Azure OpenAI Studio**: https://oai.azure.com/
2. Navigate to **Deployments** → **Create new deployment**
3. Select model: **gpt-4** or **gpt-35-turbo**
4. Note deployment name → `AZURE_OPENAI_DEPLOYMENT_NAME`

#### 2.3 Get Credentials

1. Go to **Azure Portal** → **Azure OpenAI** → **Keys and Endpoint**
2. Copy **KEY 1** → `AZURE_OPENAI_API_KEY`
3. Copy **Endpoint** → `AZURE_OPENAI_ENDPOINT`

---

### Step 3: Azure AI Search Setup (F-108)

#### 3.1 Create Search Service

```bash
az search service create \
  --name <your-search-service> \
  --resource-group <your-resource-group> \
  --sku standard \
  --location eastus
```

#### 3.2 Get Credentials

1. Go to **Azure Portal** → **Azure AI Search** → **Keys**
2. Copy **Admin Key** → `AZURE_AI_SEARCH_API_KEY`
3. Copy **Url** → `AZURE_AI_SEARCH_ENDPOINT`

#### 3.3 Create Index Schema

Use the NLWeb setup process to create the index with Schema.org types:
- `Event` (for elections)
- `VoteAction` (custom, for ballots)
- `Report` (for verification reports)
- `GovernmentOrganization` (for election authorities)

---

### Step 4: Azure Cosmos DB Setup (F-010, F-103, F-109)

#### 4.1 Create Cosmos DB Account

```bash
az cosmosdb create \
  --name <your-cosmos-account> \
  --resource-group <your-resource-group> \
  --kind MongoDB \
  --locations regionName=eastus failoverPriority=0
```

#### 4.2 Create Database

```bash
az cosmosdb mongodb database create \
  --account-name <your-cosmos-account> \
  --name ElectionGuardDb \
  --resource-group <your-resource-group>
```

#### 4.3 Get Connection String

```bash
az cosmosdb keys list \
  --name <your-cosmos-account> \
  --resource-group <your-resource-group> \
  --type connection-strings
```

Copy the connection string → `AZURE_COSMOS_DB_CONNECTION_STRING`

#### 4.4 Initialize Collections

Run the initialization script to create vSPACE collections:

```python
from pymongo import MongoClient

client = MongoClient("<CONNECTION_STRING>")
db = client["ElectionGuardDb"]

# Create collections with unique indexes
db.create_collection("vspace_serial_numbers")
db["vspace_serial_numbers"].create_index("serial_number", unique=True)
db["vspace_serial_numbers"].create_index("election_id")

db.create_collection("vspace_credentials")
db["vspace_credentials"].create_index("credential_id")
db["vspace_credentials"].create_index("election_id")

db.create_collection("vspace_bindings")
db["vspace_bindings"].create_index("ballot_id")
db["vspace_bindings"].create_index("voter_id")
```

---

### Step 5: Azure App Service Setup (F-105, F-106)

#### 5.1 Create App Service Plan

```bash
az appservice plan create \
  --name vspace-plan \
  --resource-group <your-resource-group> \
  --sku P3V2 \
  --is-linux
```

#### 5.2 Create vSpaceVote.com Web App

```bash
az webapp create \
  --resource-group <your-resource-group> \
  --plan vspace-plan \
  --name <unique-app-name-vote> \
  --runtime "PYTHON:3.9" \
  --deployment-local-git
```

#### 5.3 Create vSpaceWallet.com Web App

```bash
az webapp create \
  --resource-group <your-resource-group> \
  --plan vspace-plan \
  --name <unique-app-name-wallet> \
  --runtime "PYTHON:3.9" \
  --deployment-local-git
```

#### 5.4 Configure Environment Variables

For each web app:

```bash
az webapp config appsettings set \
  --name <app-name> \
  --resource-group <your-resource-group> \
  --settings \
    AZURE_ENTRA_TENANT_ID=<value> \
    AZURE_AD_APP_CLIENT_ID=<value> \
    AZURE_AD_APP_CLIENT_SECRET=<value> \
    AZURE_OPENAI_ENDPOINT=<value> \
    AZURE_OPENAI_API_KEY=<value> \
    VSPACE_DRY_RUN=false
```

#### 5.5 Configure Custom Domains

1. Go to **Azure Portal** → **App Service** → **Custom domains**
2. Add domain: `vspacevote.com` and `vspacewallet.com`
3. Configure DNS records as instructed
4. Enable **HTTPS** with managed certificates

#### 5.6 Configure Azure Front Door (Optional)

For DDoS protection and global CDN:

```bash
az afd profile create \
  --profile-name vspace-frontdoor \
  --resource-group <your-resource-group> \
  --sku Premium_AzureFrontDoor
```

---

## Configuration Wizard

The interactive wizard guides you through all configuration steps:

```bash
cd setup
python wizard.py
```

**Wizard Steps:**

1. **Microsoft Entra Verified ID Configuration**
   - Tenant ID
   - Client ID
   - Client Secret
   - Subscription ID (optional)

2. **Azure OpenAI Service Configuration**
   - Endpoint
   - API Key
   - Deployment name

3. **Azure AI Search Configuration**
   - Endpoint
   - API Key
   - Index name

4. **Azure Cosmos DB Configuration**
   - Connection string
   - Database name

5. **Azure App Service Configuration**
   - vSpaceVote.com app name
   - vSpaceWallet.com app name (optional)

6. **Development Mode Configuration**
   - Dry-run mode toggle
   - Log level

**Output:**

- `.env` file with your configuration
- `setup_report.json` with next steps

---

## Validation

After configuration, validate your setup:

```bash
cd setup
python validate.py [--strict]
```

**Validation Checks:**

1. Required environment variables present
2. Optional variables configured
3. Dry-run mode status
4. vSPACE-specific settings (curve, threshold)
5. Service connection tests (if not in dry-run mode)

**Validation Report:**

Saved to `validation_report.json` with:
- Timestamp
- Total checks performed
- Passed/warnings/errors count
- Configuration summary

---

## Running the E2E PoC Demo

After setup and validation:

```bash
cd demo
python run_e2e_poc.py --voters 10 --output-dir ./output
```

**Demo Phases:**

1. **Election Setup**: Generate manifest and SAAC parameters
2. **Voter Registration**: Mock Entra VC issuance
3. **Credential Derivation**: Convert Entra VC to SAAC anonymous credential
4. **Multi-Holder Splitting**: Split credentials into shares (2-of-2)
5. **Ballot Binding**: Generate binding commitments and proofs
6. **Serial Registration**: Register one-show serial numbers
7. **Record Construction**: Build augmented election record
8. **NLWeb Queries**: Test conversational interface
9. **Verification**: Validate all cryptographic artifacts

**Output Artifacts:**

- `augmented_election_record.json`: Complete election record with vSPACE extensions
- `demo_results.json`: Execution summary and verification results

---

## Troubleshooting

### Common Issues

#### 1. "Missing required variable: AZURE_ENTRA_TENANT_ID"

**Cause**: Entra Verified ID configuration not completed.

**Solution**:
```bash
python wizard.py
# Complete Step 1: Microsoft Entra Verified ID Configuration
```

#### 2. "Invalid GUID format for Tenant ID"

**Cause**: Tenant ID must be in GUID format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

**Solution**: Copy the correct value from Azure Portal → Azure Active Directory → Overview.

#### 3. "Entra VC issuance failed"

**Cause**: Missing admin consent or incorrect API permissions.

**Solution**:
1. Verify `VerifiableCredential.Create.All` permission is granted
2. Ensure admin consent has been approved
3. Check that the app registration is not expired

#### 4. "Duplicate serial number detected"

**Cause**: Demo attempting to register same serial twice (should not happen in normal flow).

**Solution**: This is a critical error. Check the `demo_results.json` for details and re-run with different random seed.

#### 5. "Cosmos DB connection failed"

**Cause**: Invalid connection string or firewall blocking access.

**Solution**:
1. Verify connection string format
2. Check Cosmos DB firewall settings (allow Azure services)
3. Ensure your IP is whitelisted if using private endpoint

### Dry-Run Mode Issues

#### "Mock connection test failed"

**Cause**: Dry-run mode should skip actual API calls.

**Solution**: Ensure `VSPACE_DRY_RUN=true` in your `.env` file.

### Production Mode Issues

#### "OAuth2 token acquisition failed"

**Cause**: Invalid client credentials or expired secret.

**Solution**:
1. Regenerate client secret in Azure AD app registration
2. Update `.env` with new secret
3. Restart application

#### "DID document not resolvable"

**Cause**: `did.json` not properly hosted or DNS misconfigured.

**Solution**:
1. Verify `https://vspacevote.com/.well-known/did.json` is accessible
2. Check DNS records for vspacevote.com
3. Ensure HTTPS certificate is valid

### Getting Help

For additional support:

1. Check validation report: `setup/validation_report.json`
2. Review demo results: `demo/output/demo_results.json`
3. Enable debug logging: Set `VSPACE_LOG_LEVEL=DEBUG` in `.env`
4. Consult README.md for architecture details

---

## Next Steps

After successful setup:

1. **Deploy to Production**:
   - Disable dry-run mode
   - Configure production monitoring (Application Insights)
   - Set up auto-scaling for App Service

2. **Run Large-Scale Simulation**:
   ```bash
   python run_e2e_poc.py --voters 100
   ```

3. **Integrate with ElectionGuard API**:
   - Mount vSPACE FastAPI sub-application
   - Configure `/v1/vspace/` endpoint group

4. **Security Audit**:
   - Review all cryptographic implementations
   - Validate one-show enforcement under load
   - Test cross-origin security boundaries

5. **NLWeb Indexing**:
   - Index election manifest and sample records
   - Configure Schema.org types
   - Test MCP server endpoint

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-04-13  
**Related Documents**: README.md, vSPACE_Augmented_PRD_v260412a.json
