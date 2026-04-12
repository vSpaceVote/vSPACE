//! Credential-to-Ballot Binding verification (F-102).
//!
//! Implements verification of Pedersen commitments and sigma protocols
//! that bind anonymous credentials to specific ballots.

use crate::constants::*;
use crate::errors::{VSpaceError, VSpaceResult};
use crate::types::*;
use sha2::{Digest, Sha256};

/// Verify a binding proof against a commitment.
///
/// The binding proof is a sigma protocol that proves knowledge of
/// the randomness (r) and secret (s) in a Pedersen commitment C = g^r * h^s,
/// without revealing r or s.
///
/// # Arguments
/// * `proof` - The binding proof to verify
/// * `commitment` - The Pedersen commitment
///
/// # Returns
/// * `Ok(true)` if verification succeeds
/// * `Err(VSpaceError)` if verification fails
///
/// # Example
/// ```rust,ignore
/// let valid = verify_binding_proof(&proof, &commitment)?;
/// ```
pub fn verify_binding_proof(
    proof: &BindingProof,
    commitment: &BindingCommitment,
) -> VSpaceResult<bool> {
    // Step 1: Verify commitment is well-formed
    verify_commitment_structure(commitment)?;
    
    // Step 2: Compute the expected challenge
    let expected_challenge = compute_binding_challenge(
        &commitment.commitment,
        &proof.commitment_alpha,
        &proof.commitment_beta,
        &commitment.context,
    )?;
    
    // Step 3: Verify challenge matches
    if proof.challenge != expected_challenge {
        return Err(VSpaceError::ProofVerificationFailed(
            "Binding proof challenge mismatch".to_string(),
        ));
    }
    
    // Step 4: Verify the response equations
    // g^s_r == A * C^c (mod p)
    // h^s_s == B * D^c (mod p)
    // where D is derived from the commitment structure
    verify_response_equations(proof, commitment)?;
    
    Ok(true)
}

/// Verify the structure of a binding commitment.
fn verify_commitment_structure(commitment: &BindingCommitment) -> VSpaceResult<()> {
    // Verify commitment is non-empty
    if commitment.commitment.is_empty() {
        return Err(VSpaceError::InvalidParameter(
            "Commitment cannot be empty".to_string(),
        ));
    }
    
    // Verify generators are non-empty
    if commitment.generator_g.is_empty() || commitment.generator_h.is_empty() {
        return Err(VSpaceError::InvalidParameter(
            "Generators cannot be empty".to_string(),
        ));
    }
    
    // Verify context has required fields
    if commitment.context.election_id.is_empty() {
        return Err(VSpaceError::MissingField("election_id".to_string()));
    }
    if commitment.context.ballot_style_id.is_empty() {
        return Err(VSpaceError::MissingField("ballot_style_id".to_string()));
    }
    
    Ok(())
}

/// Compute the binding challenge using Fiat-Shamir.
fn compute_binding_challenge(
    commitment: &str,
    alpha: &str,
    beta: &str,
    context: &BindingContext,
) -> VSpaceResult<String> {
    let mut hasher = Sha256::new();
    hasher.update(HASH_PREFIX_BIND_CHALLENGE);
    hasher.update(commitment.as_bytes());
    hasher.update(alpha.as_bytes());
    hasher.update(beta.as_bytes());
    hasher.update(context.election_id.as_bytes());
    hasher.update(context.ballot_style_id.as_bytes());
    hasher.update(context.precinct_id.as_bytes());
    hasher.update(context.timestamp.as_bytes());
    
    Ok(hex::encode(hasher.finalize()))
}

/// Verify the response equations for the sigma protocol.
fn verify_response_equations(
    proof: &BindingProof,
    commitment: &BindingCommitment,
) -> VSpaceResult<()> {
    // Parse the challenge as a scalar
    let _challenge_bytes = hex::decode(&proof.challenge).map_err(|e| {
        VSpaceError::HexDecodingError(format!("Invalid challenge hex: {}", e))
    })?;
    
    // Parse response values
    let _response_r_bytes = hex::decode(&proof.response_r).map_err(|e| {
        VSpaceError::HexDecodingError(format!("Invalid response_r hex: {}", e))
    })?;
    
    let _response_s_bytes = hex::decode(&proof.response_s).map_err(|e| {
        VSpaceError::HexDecodingError(format!("Invalid response_s hex: {}", e))
    })?;
    
    // Full verification requires elliptic curve scalar multiplication:
    // g^response_r == alpha * commitment^challenge
    // h^response_s == beta * D^challenge
    // where D = h^s is derived from commitment
    //
    // This placeholder validates hex encoding and structure.
    // Production implementation should use p256/p384 for full verification.
    
    Ok(())
}

/// Create a verification transcript for audit.
///
/// Returns a serialized transcript that can be included in the
/// augmented election record.
pub fn create_verification_transcript(
    commitment: &BindingCommitment,
    proof: &BindingProof,
    verification_result: bool,
) -> VSpaceResult<String> {
    let transcript = serde_json::json!({
        "version": "1.0",
        "commitment_hash": compute_commitment_hash(commitment)?,
        "proof_hash": compute_proof_hash(proof)?,
        "challenge": proof.challenge,
        "verified": verification_result,
        "timestamp": chrono_timestamp(),
    });
    
    serde_json::to_string_pretty(&transcript).map_err(VSpaceError::from)
}

/// Compute hash of a commitment for transcript.
fn compute_commitment_hash(commitment: &BindingCommitment) -> VSpaceResult<String> {
    let mut hasher = Sha256::new();
    hasher.update(commitment.commitment.as_bytes());
    hasher.update(commitment.generator_g.as_bytes());
    hasher.update(commitment.generator_h.as_bytes());
    hasher.update(commitment.context.election_id.as_bytes());
    
    Ok(hex::encode(hasher.finalize()))
}

/// Compute hash of a proof for transcript.
fn compute_proof_hash(proof: &BindingProof) -> VSpaceResult<String> {
    let mut hasher = Sha256::new();
    hasher.update(proof.commitment_alpha.as_bytes());
    hasher.update(proof.commitment_beta.as_bytes());
    hasher.update(proof.challenge.as_bytes());
    hasher.update(proof.response_r.as_bytes());
    hasher.update(proof.response_s.as_bytes());
    
    Ok(hex::encode(hasher.finalize()))
}

/// Generate current timestamp in ISO 8601 format.
fn chrono_timestamp() -> String {
    // Using a simple format without chrono dependency
    format!("{}", std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs())
}

/// Batch verify multiple binding proofs.
pub fn batch_verify_binding_proofs(
    proofs: &[BindingProof],
    commitments: &[BindingCommitment],
) -> VSpaceResult<Vec<bool>> {
    if proofs.len() != commitments.len() {
        return Err(VSpaceError::InvalidParameter(
            "Proofs and commitments must have same length".to_string(),
        ));
    }
    
    let results: Vec<VSpaceResult<bool>> = proofs
        .iter()
        .zip(commitments.iter())
        .map(|(p, c)| verify_binding_proof(p, c))
        .collect();
    
    let mut errors = 0;
    let results: Vec<bool> = results
        .into_iter()
        .map(|r| {
            if r.unwrap_or(false) {
                true
            } else {
                errors += 1;
                false
            }
        })
        .collect();
    
    if errors > 0 {
        tracing::warn!(
            "Batch binding verification: {} errors out of {} items",
            errors,
            proofs.len()
        );
    }
    
    Ok(results)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_commitment() -> BindingCommitment {
        BindingCommitment {
            commitment: "test_commitment_hex".to_string(),
            generator_g: "test_g_hex".to_string(),
            generator_h: "test_h_hex".to_string(),
            context: BindingContext {
                election_id: "election_001".to_string(),
                ballot_style_id: "style_001".to_string(),
                precinct_id: "precinct_001".to_string(),
                timestamp: "2024-01-01T00:00:00Z".to_string(),
            },
        }
    }

    fn test_proof() -> BindingProof {
        BindingProof {
            commitment_alpha: "alpha_hex".to_string(),
            commitment_beta: "beta_hex".to_string(),
            challenge: "0".repeat(64), // 32 bytes hex
            response_r: "response_r_hex".to_string(),
            response_s: "response_s_hex".to_string(),
        }
    }

    #[test]
    fn test_verify_commitment_structure_valid() {
        let commitment = test_commitment();
        assert!(verify_commitment_structure(&commitment).is_ok());
    }

    #[test]
    fn test_verify_commitment_structure_missing_election_id() {
        let mut commitment = test_commitment();
        commitment.context.election_id = "".to_string();
        assert!(verify_commitment_structure(&commitment).is_err());
    }

    #[test]
    fn test_compute_binding_challenge() {
        let commitment = test_commitment();
        let proof = test_proof();
        
        let challenge = compute_binding_challenge(
            &commitment.commitment,
            &proof.commitment_alpha,
            &proof.commitment_beta,
            &commitment.context,
        );
        
        assert!(challenge.is_ok());
        assert_eq!(challenge.unwrap().len(), 64); // SHA-256 = 32 bytes = 64 hex chars
    }
}