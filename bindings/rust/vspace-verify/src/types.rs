//! Type definitions for vSPACE data structures.

use serde::{Deserialize, Serialize};

/// SAAC issuer public parameters (F-100)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SAACIssuerParams {
    /// Curve identifier: "P-256" or "P-384"
    pub curve: String,
    /// Generator G as hex-encoded point
    pub generator_g: String,
    /// Generator H as hex-encoded point
    pub generator_h: String,
    /// Generator G_tilde for credential derivation
    pub generator_g_tilde: String,
    /// Generator H_tilde for credential derivation
    pub generator_h_tilde: String,
    /// Issuer public key Y as hex-encoded point
    pub issuer_public_key: String,
    /// SHA-256 hash of all parameters for integrity
    pub params_hash: String,
}

/// SAAC credential issued to holder (F-100)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SAACCredential {
    /// Credential ID (random nonce)
    pub credential_id: String,
    /// Secret exponent a (hex-encoded)
    pub secret_a: String,
    /// Secret exponent b (hex-encoded)
    pub secret_b: String,
    /// Issuer signature component sigma_a (hex-encoded point)
    pub sigma_a: String,
    /// Issuer signature component sigma_b (hex-encoded point)
    pub sigma_b: String,
    /// Issuance timestamp (ISO 8601)
    pub issued_at: String,
}

/// SAAC presentation for verification (F-100)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SAACPresentation {
    /// Credential ID being presented
    pub credential_id: String,
    /// Revealed commitment C = G^a * H^b
    pub commitment: String,
    /// Schnorr proof of knowledge of (a, b)
    pub pok: SchnorrProof,
    /// Issuer signature proof
    pub issuer_sig_proof: IssuerSignatureProof,
    /// Presentation timestamp (ISO 8601)
    pub presented_at: String,
}

/// Schnorr proof of knowledge
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchnorrProof {
    /// Challenge c = H(G, H, C, R1, R2)
    pub challenge: String,
    /// Response s_a for secret a
    pub response_a: String,
    /// Response s_b for secret b
    pub response_b: String,
    /// Random commitment R1 = G^r1
    pub random_commitment_r1: String,
    /// Random commitment R2 = H^r2
    pub random_commitment_r2: String,
}

/// Issuer signature proof (NIZK that credential was signed by issuer)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IssuerSignatureProof {
    /// Proof that sigma_a, sigma_b are valid issuer signatures
    pub challenge: String,
    pub response: String,
}

/// Binding commitment for credential-to-ballot binding (F-102)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BindingCommitment {
    /// Pedersen commitment C = g^r * h^s
    pub commitment: String,
    /// Generator g (hex-encoded point)
    pub generator_g: String,
    /// Generator h (hex-encoded point)
    pub generator_h: String,
    /// Binding context (election ID, ballot style, etc.)
    pub context: BindingContext,
}

/// Context for binding commitment
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BindingContext {
    /// Election identifier
    pub election_id: String,
    /// Ballot style identifier
    pub ballot_style_id: String,
    /// Precinct or district identifier
    pub precinct_id: String,
    /// Timestamp of binding
    pub timestamp: String,
}

/// Binding proof (sigma protocol for binding verification)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BindingProof {
    /// Commitment to randomness A = g^alpha
    pub commitment_alpha: String,
    /// Commitment to secret B = h^beta
    pub commitment_beta: String,
    /// Challenge c = H(C, A, B, context)
    pub challenge: String,
    /// Response s_r for randomness r
    pub response_r: String,
    /// Response s_s for secret s
    pub response_s: String,
}

/// VRF-derived serial number (F-103)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VRFSerial {
    /// Serial number (hex-encoded, typically 32 bytes)
    pub serial: String,
    /// VRF public key used for derivation
    pub vrf_public_key: String,
    /// VRF proof (hex-encoded)
    pub vrf_proof: String,
    /// Derivation context
    pub context: String,
}

/// Serial number registry entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SerialRegistryEntry {
    /// Serial number
    pub serial: String,
    /// Election ID
    pub election_id: String,
    /// Registration timestamp (ISO 8601)
    pub registered_at: String,
    /// Verification status
    pub status: SerialStatus,
}

/// Status of a serial number in the registry
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum SerialStatus {
    /// Serial is valid and unused
    Valid,
    /// Serial has been used (one-show violation)
    Used,
    /// Serial is invalid (failed verification)
    Invalid,
}

/// Augmented election record extension (F-109)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AugmentedRecord {
    /// vSPACE extension version
    pub version: String,
    /// SAAC issuer parameters hash
    pub issuer_params_hash: String,
    /// All serial numbers used in this election
    pub serial_numbers: Vec<String>,
    /// Binding commitments for all ballots
    pub binding_commitments: Vec<BindingCommitment>,
    /// Verification results summary
    pub verification_summary: VerificationSummary,
}

/// Summary of verification results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationSummary {
    /// Total number of ballots processed
    pub total_ballots: u64,
    /// Number of unique serial numbers
    pub unique_serials: u64,
    /// Number of duplicate serials detected (should be 0)
    pub duplicate_serials: u64,
    /// Number of valid binding proofs
    pub valid_binding_proofs: u64,
    /// Number of invalid binding proofs
    pub invalid_binding_proofs: u64,
    /// All presentations valid
    pub all_presentations_valid: bool,
}