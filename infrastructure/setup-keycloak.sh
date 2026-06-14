#!/bin/bash
# Keycloak Configuration for vSPACE
# This script sets up the vSPACE realm with clients and roles

KEYCLOAK_URL="http://localhost:8180"
REALM_NAME="vspace"
ADMIN_USER="admin"
ADMIN_PASS="admin"

echo "Getting admin token..."
TOKEN=$(curl -s -X POST ${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${ADMIN_USER}" \
  -d "password=${ADMIN_PASS}" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Creating vSPACE realm..."
curl -s -X POST ${KEYCLOAK_URL}/admin/realms \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "realm": "'${REALM_NAME}'",
    "enabled": true,
    "displayName": "vSPACE",
    "displayNameHtml": "<strong>vSPACE</strong>",
    "registrationAllowed": false,
    "loginWithEmailAllowed": true,
    "duplicateEmailsAllowed": false,
    "resetPasswordAllowed": true,
    "editUsernameAllowed": false,
    "bruteForceProtected": true,
    "permanentLockout": false,
    "maxFailureWaitSeconds": 900,
    "minimumQuickLoginWaitSeconds": 60,
    "waitIncrementSeconds": 60,
    "quickLoginCheckMilliSeconds": 1000,
    "maxDeltaTimeSeconds": 43200,
    "failureFactor": 5,
    "passwordPolicy": "length(8) and upperCase(1) and lowerCase(1) and digits(1)"
  }'

echo ""
echo "Creating vSpaceVote client..."
curl -s -X POST ${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "vspacevote",
    "name": "vSpaceVote.com",
    "description": "vSpaceVote.com Voter Facing PWA",
    "enabled": true,
    "clientAuthenticatorType": "client-secret",
    "secret": "vspacevote-secret-key-2026",
    "redirectUris": [
      "https://vspacevote.com/*",
      "http://localhost:3000/*"
    ],
    "webOrigins": [
      "https://vspacevote.com",
      "http://localhost:3000"
    ],
    "standardFlowEnabled": true,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": true,
    "serviceAccountsEnabled": false,
    "publicClient": false,
    "protocol": "openid-connect",
    "fullScopeAllowed": true,
    "attributes": {
      "post.logout.redirect.uris": "https://vspacevote.com/*"
    }
  }'

echo ""
echo "Creating vSpaceWallet client..."
curl -s -X POST ${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "vspacewallet",
    "name": "vSpaceWallet.com",
    "description": "vSpaceWallet.com Credential Wallet PWA",
    "enabled": true,
    "clientAuthenticatorType": "client-secret",
    "secret": "vspacewallet-secret-key-2026",
    "redirectUris": [
      "https://vspacewallet.com/*",
      "http://localhost:3001/*"
    ],
    "webOrigins": [
      "https://vspacewallet.com",
      "http://localhost:3001"
    ],
    "standardFlowEnabled": true,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": true,
    "serviceAccountsEnabled": false,
    "publicClient": false,
    "protocol": "openid-connect",
    "fullScopeAllowed": true,
    "attributes": {
      "post.logout.redirect.uris": "https://vspacewallet.com/*"
    }
  }'

echo ""
echo "Creating roles..."

# Voter role
curl -s -X POST ${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/roles \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "voter",
    "description": "Registered voter with eligibility to vote",
    "composite": false,
    "clientRole": false,
    "containerId": "'${REALM_NAME}'"
  }'

# Election Officer role
curl -s -X POST ${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/roles \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "election-officer",
    "description": "Election officer with administrative privileges",
    "composite": false,
    "clientRole": false,
    "containerId": "'${REALM_NAME}'"
  }'

# Auditor role
curl -s -X POST ${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/roles \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "auditor",
    "description": "Auditor with read-only access to election records",
    "composite": false,
    "clientRole": false,
    "containerId": "'${REALM_NAME}'"
  }'

echo ""
echo "Creating test users..."

# Test voter
curl -s -X POST ${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "voter1",
    "email": "voter1@vspacevote.com",
    "firstName": "Test",
    "lastName": "Voter",
    "enabled": true,
    "emailVerified": true,
    "credentials": [{
      "type": "password",
      "value": "voter123",
      "temporary": false
    }]
  }'

echo ""
echo "Keycloak configuration complete!"
echo ""
echo "Keycloak Admin Console: ${KEYCLOAK_URL}/admin"
echo "Realm: ${REALM_NAME}"
echo ""
echo "Client IDs:"
echo "  - vspacevote (secret: vspacevote-secret-key-2026)"
echo "  - vspacewallet (secret: vspacewallet-secret-key-2026)"
echo ""
echo "Test User:"
echo "  - username: voter1"
echo "  - password: voter123"
