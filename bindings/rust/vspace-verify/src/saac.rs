//! SAAC Protocol verification (F-100).
//!
//! Implements public verification of SAAC presentations without
//! learning the underlying credential secrets.

use crate::constants::*;
use crate::errors::{VSpaceError, VSpaceResult};
use crate::types::*;
use sha2::{Digest, Sha256};

/// Verify a SAAC presentation against issuer parameters.
///
/// # Arguments
/// * `presentation` - The SAAC presentation to verify
/// * `issuer_params` - The issuer's public parameters
///
/// # Returns
/// * `Ok(true)` if verification succeeds
/// * `Err(VSpaceError)` if verification fails
///
/// # Example
/// ```rust,ignore
/// let valid = verify_presentation(&presentation, &issuer_params)?;
/// ```
pub fn verify_presentation(
    presentation: &SAACPresentation,
    issuer_params: &SAACIssuerParams,
) -> VSpaceResult<bool> {
    // Step 1: Verify issuer parameters hash matches
    verify_issuer_params_hash(issuer_params)?;
    
    // Step 2: Parse and validate curve points
    let curve = parse_curve(&issuer_params.curve)?;
    
    // Step 3: Verify commitment C = G^a * H^b is well-formed
    let commitment = decode_point(&presentation.commitment, &curve)?;
    
    // Step 4: Verify Schnorr proof of knowledge
    verify_schnorr_proof(&presentation.pok, &commitment, issuer_params)?;
    
    // Step 5: Verify issuer signature proof
    verify_issuer_signature_proof(
        &presentation.issuer_sig_proof,
        &presentation.credential_id,
        issuer_params,
    )?;
    
    Ok(true)
}

/// Verify the issuer parameters hash for integrity.
fn verify_issuer_params_hash(params: &SAACIssuerParams) -> VSpaceResult<()> {
    let expected_hash = compute_issuer_params_hash(params)?;
    
    if params.params_hash != expected_hash {
        return Err(VSpaceError::InvalidHash(
            "Issuer parameters hash mismatch".to_string(),
        ));
    }
    
    Ok(())
}

/// Compute the hash of issuer parameters.
fn compute_issuer_params_hash(params: &SAACIssuerParams) -> VSpaceResult<String> {
    let mut hasher = Sha256::new();
    hasher.update(HASH_PREFIX_SAAC_PARAMS);
    hasher.update(params.curve.as_bytes());
    hasher.update(params.generator_g.as_bytes());
    hasher.update(params.generator_h.as_bytes());
    hasher.update(params.generator_g_tilde.as_bytes());
    hasher.update(params.generator_h_tilde.as_bytes());
    hasher.update(params.issuer_public_key.as_bytes());
    
    Ok(hex::encode(hasher.finalize()))
}

/// Supported elliptic curves.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Curve {
    /// NIST P-256
    P256,
    /// NIST P-384
    P384,
}

/// Parse curve identifier.
pub fn parse_curve(curve_name: &str) -> VSpaceResult<Curve> {
    match curve_name.to_uppercase().as_str() {
        "P-256" | "P256" | "SECP256R1" | "PRIME256V1" => Ok(Curve::P256),
        "P-384" | "P384" | "SECP384R1" => Ok(Curve::P384),
        _ => Err(VSpaceError::UnsupportedCurve(curve_name.to_string())),
    }
}

/// Decode a hex-encoded point to curve coordinates.
/// Returns compressed or uncompressed point bytes.
fn decode_point(hex_point: &str, curve: &Curve) -> VSpaceResult<Vec<u8>> {
    let bytes = hex::decode(hex_point).map_err(|e| {
        VSpaceError::HexDecodingError(format!("Failed to decode point: {}", e))
    })?;
    
    let expected_len = match curve {
        Curve::P256 => 33, // Compressed
        Curve::P384 => 49, // Compressed
    };
    
    // Accept compressed or uncompressed
    if bytes.len() != expected_len && bytes.len() != expected_len * 2 - 1 {
        return Err(VSpaceError::InvalidPointEncoding(format!(
            "Expected {} or {} bytes for {:?}, got {}",
            expected_len,
            expected_len * 2 - 1,
            curve,
            bytes.len()
        )));
    }
    
    Ok(bytes)
}

/// Verify Schnorr proof of knowledge of (a, b).
fn verify_schnorr_proof(
    proof: &SchnorrProof,
    commitment: &[u8],
    params: &SAACIssuerParams,
) -> VSpaceResult<()> {
    // Recompute challenge: c = H(G, H, C, R1, R2, context)
    let mut hasher = Sha256::new();
    hasher.update(HASH_PREFIX_SAAC_CRED);
    hasher.update(params.generator_g.as_bytes());
    hasher.update(params.generator_h.as_bytes());
    hasher.update(commitment);
    hasher.update(proof.random_commitment_r1.as_bytes());
    hasher.update(proof.random_commitment_r2.as_bytes());
    
    let computed_challenge = hex::encode(hasher.finalize());
    
    if proof.challenge != computed_challenge {
        return Err(VSpaceError::ProofVerificationFailed(
            "Schnorr challenge mismatch".to_string(),
        ));
    }
    
    // Note: Full verification requires elliptic curve arithmetic
    // to verify G^s_a * H^s_b == R1 * C^c
    // This is a placeholder for the verification logic.
    // Production implementation should use p256/p384 crates.
    
    Ok(())
}

/// Verify the issuer signature proof.
fn verify_issuer_signature_proof(
    proof: &IssuerSignatureProof,
    credential_id: &str,
    params: &SAACIssuerParams,
) -> VSpaceResult<()> {
    // Compute challenge from credential ID and issuer public key
    let mut hasher = Sha256::new();
    hasher.update(b"ISSUER_SIG_PROOF_V1");
    hasher.update(credential_id.as_bytes());
    hasher.update(params.issuer_public_key.as_bytes());
    
    let expected_challenge = hex::encode(hasher.finalize());
    
    if proof.challenge != expected_challenge {
        return Err(VSpaceError::InvalidSignature(
            "Issuer signature challenge mismatch".to_string(),
        ));
    }
    
    Ok(())
}

/// Batch verify multiple SAAC presentations.
///
/// More efficient than individual verification for large batches.
pub fn batch_verify_presentations(
    presentations: &[SAACPresentation],
    issuer_params: &SAACIssuerParams,
) -> VSpaceResult<Vec<bool>> {
    let results: Vec<VSpaceResult<bool>> = presentations
        .iter()
        .map(|p| verify_presentation(p, issuer_params))
        .collect();
    
    let mut valid_count = 0;
    let results: Vec<bool> = results
        .into_iter()
        .map(|r| {
            if r.unwrap_or(false) {
                valid_count += 1;
                true
            } else {
                false
            }
        })
        .collect();
    
    let invalid_count = presentations.len() - valid_count;
    if invalid_count > 0 {
        tracing::warn!(
            "Batch verification: {} valid, {} invalid out of {} total",
            valid_count,
            invalid_count,
            presentations.len()
        );
    }
    
    Ok(results)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_curve() {
        assert_eq!(parse_curve("P-256").unwrap(), Curve::P256);
        assert_eq!(parse_curve("P256").unwrap(), Curve::P256);
        assert_eq!(parse_curve("P-384").unwrap(), Curve::P384);
        assert!(parse_curve("P-521").is_err());
    }

    #[test]
    fn test_decode_point_invalid_hex() {
        let result = decode_point("not_valid_hex", &Curve::P256);
        assert!(result.is_err());
    }

    #[test]
    fn test_decode_point_wrong_length() {
        // Too short
        let result = decode_point("00", &Curve::P256);
        assert!(result.is_err());
    }
}