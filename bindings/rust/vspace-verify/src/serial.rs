//! One-Show Serial Uniqueness verification (F-103).
//!
//! Implements VRF-derived serial number verification and duplicate detection.

use crate::constants::*;
use crate::errors::{VSpaceError, VSpaceResult};
use crate::types::*;
use sha2::{Digest, Sha256};
use std::collections::HashSet;

/// Verify a VRF-derived serial number.
///
/// # Arguments
/// * `serial` - The VRF serial to verify
///
/// # Returns
/// * `Ok(true)` if verification succeeds
/// * `Err(VSpaceError)` if verification fails
pub fn verify_vrf_serial(serial: &VRFSerial) -> VSpaceResult<bool> {
    // Step 1: Verify serial length is within bounds
    let serial_bytes = hex::decode(&serial.serial).map_err(|e| {
        VSpaceError::HexDecodingError(format!("Invalid serial hex: {}", e))
    })?;
    
    if serial_bytes.len() < MIN_SERIAL_LENGTH {
        return Err(VSpaceError::InvalidParameter(format!(
            "Serial too short: {} bytes, minimum {}",
            serial_bytes.len(),
            MIN_SERIAL_LENGTH
        )));
    }
    
    if serial_bytes.len() > MAX_SERIAL_LENGTH {
        return Err(VSpaceError::InvalidParameter(format!(
            "Serial too long: {} bytes, maximum {}",
            serial_bytes.len(),
            MAX_SERIAL_LENGTH
        )));
    }
    
    // Step 2: Verify VRF proof (placeholder for full VRF verification)
    verify_vrf_proof(&serial.vrf_proof, &serial.vrf_public_key, &serial.context)?;
    
    // Step 3: Verify serial derivation matches VRF output
    let expected_serial = derive_serial_from_vrf(&serial.vrf_proof, &serial.context)?;
    
    if serial.serial != expected_serial {
        return Err(VSpaceError::VerificationFailed(
            "Serial does not match VRF derivation".to_string(),
        ));
    }
    
    Ok(true)
}

/// Verify the VRF proof.
fn verify_vrf_proof(
    proof: &str,
    public_key: &str,
    context: &str,
) -> VSpaceResult<()> {
    // Decode proof and public key
    let _proof_bytes = hex::decode(proof).map_err(|e| {
        VSpaceError::HexDecodingError(format!("Invalid VRF proof hex: {}", e))
    })?;
    
    let _pk_bytes = hex::decode(public_key).map_err(|e| {
        VSpaceError::HexDecodingError(format!("Invalid VRF public key hex: {}", e))
    })?;
    
    // Full VRF verification requires:
    // 1. Parse VRF public key
    // 2. Verify proof against public key and context
    // 3. Ensure proof is correctly formed
    //
    // This placeholder validates hex encoding.
    // Production implementation should use a VRF library like curve25519-dalek.
    
    Ok(())
}

/// Derive the expected serial from VRF output.
fn derive_serial_from_vrf(proof: &str, context: &str) -> VSpaceResult<String> {
    let mut hasher = Sha256::new();
    hasher.update(HASH_PREFIX_VRF_SERIAL);
    hasher.update(proof.as_bytes());
    hasher.update(context.as_bytes());
    
    Ok(hex::encode(hasher.finalize()))
}

/// Check serial uniqueness against a registry.
///
/// # Arguments
/// * `serial` - The serial number to check
/// * `registry` - Set of previously seen serials
///
/// # Returns
/// * `Ok(true)` if serial is unique (not in registry)
/// * `Ok(false)` if serial already exists (duplicate)
pub fn check_serial_uniqueness(serial: &str, registry: &HashSet<String>) -> bool {
    !registry.contains(serial)
}

/// Detect duplicates in a batch of serials.
///
/// Uses O(n log n) algorithm based on sorting.
///
/// # Arguments
/// * `serials` - Slice of serial number strings
///
/// # Returns
/// * Vector of duplicate serial numbers (if any)
pub fn detect_duplicates(serials: &[String]) -> Vec<String> {
    let mut seen = HashSet::new();
    let mut duplicates = Vec::new();
    
    for serial in serials {
        if !seen.insert(serial.clone()) {
            duplicates.push(serial.clone());
        }
    }
    
    duplicates
}

/// Verify serial uniqueness for a batch.
///
/// # Arguments
/// * `serials` - Slice of VRFSerial objects
///
/// # Returns
/// * `Ok(())` if all serials are unique
/// * `Err(VSpaceError::DuplicateSerial)` if duplicates found
pub fn verify_serial_uniqueness(serials: &[VRFSerial]) -> VSpaceResult<()> {
    let serial_strings: Vec<String> = serials.iter().map(|s| s.serial.clone()).collect();
    
    let duplicates = detect_duplicates(&serial_strings);
    
    if !duplicates.is_empty() {
        return Err(VSpaceError::DuplicateSerial(format!(
            "Found {} duplicate serials: {}",
            duplicates.len(),
            duplicates.join(", ")
        )));
    }
    
    Ok(())
}

/// Batch verify VRF serials.
///
/// More efficient than individual verification for large batches.
pub fn batch_verify_vrf_serials(serials: &[VRFSerial]) -> VSpaceResult<Vec<bool>> {
    // First check for duplicates
    verify_serial_uniqueness(serials)?;
    
    // Then verify each VRF proof
    let results: Vec<VSpaceResult<bool>> = serials
        .iter()
        .map(|s| verify_vrf_serial(s))
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
            "Batch VRF verification: {} errors out of {} serials",
            errors,
            serials.len()
        );
    }
    
    Ok(results)
}

/// Serial registry for tracking used serials.
///
/// This is an in-memory implementation. Production use should
/// back this with a persistent database (MongoDB as specified in PRD).
#[derive(Debug, Clone, Default)]
pub struct SerialRegistry {
    used_serials: HashSet<String>,
}

impl SerialRegistry {
    /// Create a new empty registry.
    pub fn new() -> Self {
        Self {
            used_serials: HashSet::new(),
        }
    }
    
    /// Register a serial number.
    ///
    /// # Returns
    /// * `Ok(true)` if serial was successfully registered
    /// * `Ok(false)` if serial was already registered (one-show violation)
    pub fn register(&mut self, serial: &str) -> VSpaceResult<bool> {
        if self.used_serials.contains(serial) {
            return Err(VSpaceError::SerialAlreadyUsed(serial.to_string()));
        }
        self.used_serials.insert(serial.to_string());
        Ok(true)
    }
    
    /// Check if a serial is already registered.
    pub fn is_registered(&self, serial: &str) -> bool {
        self.used_serials.contains(serial)
    }
    
    /// Get the count of registered serials.
    pub fn len(&self) -> usize {
        self.used_serials.len()
    }
    
    /// Check if the registry is empty.
    pub fn is_empty(&self) -> bool {
        self.used_serials.is_empty()
    }
    
    /// Clear all registered serials.
    pub fn clear(&mut self) {
        self.used_serials.clear();
    }
    
    /// Get all registered serials.
    pub fn all_serials(&self) -> Vec<String> {
        self.used_serials.iter().cloned().collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_vrf_serial(serial_hex: &str) -> VRFSerial {
        VRFSerial {
            serial: serial_hex.to_string(),
            vrf_public_key: "00".repeat(32), // 32 bytes
            vrf_proof: "ff".repeat(64),       // 64 bytes
            context: "test_context".to_string(),
        }
    }

    #[test]
    fn test_serial_registry_basic() {
        let mut registry = SerialRegistry::new();
        
        // First registration succeeds
        assert!(registry.register("serial_001").unwrap());
        assert!(registry.is_registered("serial_001"));
        
        // Second registration of same serial fails
        assert!(registry.register("serial_001").is_err());
        
        // Different serial succeeds
        assert!(registry.register("serial_002").unwrap());
    }

    #[test]
    fn test_detect_duplicates_empty() {
        let serials: Vec<String> = vec![];
        let duplicates = detect_duplicates(&serials);
        assert!(duplicates.is_empty());
    }

    #[test]
    fn test_detect_duplicates_none() {
        let serials = vec![
            "serial_001".to_string(),
            "serial_002".to_string(),
            "serial_003".to_string(),
        ];
        let duplicates = detect_duplicates(&serials);
        assert!(duplicates.is_empty());
    }

    #[test]
    fn test_detect_duplicates_found() {
        let serials = vec![
            "serial_001".to_string(),
            "serial_002".to_string(),
            "serial_001".to_string(), // duplicate
            "serial_003".to_string(),
        ];
        let duplicates = detect_duplicates(&serials);
        assert_eq!(duplicates.len(), 1);
        assert_eq!(duplicates[0], "serial_001");
    }

    #[test]
    fn test_check_serial_uniqueness() {
        let mut registry = HashSet::new();
        registry.insert("serial_001".to_string());
        
        assert!(!check_serial_uniqueness("serial_001", &registry));
        assert!(check_serial_uniqueness("serial_002", &registry));
    }
}