//! Cryptographic constants for vSPACE verification.

use num_bigint::BigUint;

/// NIST P-256 curve order
pub const P256_ORDER_HEX: &str = "ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551";

/// NIST P-384 curve order  
pub const P384_ORDER_HEX: &str = "ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973";

/// BLS12-381 scalar field order (first 64 hex digits)
pub const BLS12_381_ORDER_HEX: &str = "73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001";

/// Hash prefix for SAAC parameter derivation (UTF-8 "SAAC_PARAMS_V1")
pub const HASH_PREFIX_SAAC_PARAMS: &[u8] = b"SAAC_PARAMS_V1";

/// Hash prefix for credential derivation (UTF-8 "SAAC_CRED_V1")
pub const HASH_PREFIX_SAAC_CRED: &[u8] = b"SAAC_CRED_V1";

/// Hash prefix for binding commitment (UTF-8 "BIND_COMMIT_V1")
pub const HASH_PREFIX_BIND_COMMIT: &[u8] = b"BIND_COMMIT_V1";

/// Hash prefix for binding challenge (UTF-8 "BIND_CHALLENGE_V1")
pub const HASH_PREFIX_BIND_CHALLENGE: &[u8] = b"BIND_CHALLENGE_V1";

/// Hash prefix for VRF serial derivation (UTF-8 "VRF_SERIAL_V1")
pub const HASH_PREFIX_VRF_SERIAL: &[u8] = b"VRF_SERIAL_V1";

/// Minimum serial number length in bytes
pub const MIN_SERIAL_LENGTH: usize = 16;

/// Maximum serial number length in bytes
pub const MAX_SERIAL_LENGTH: usize = 64;

/// Maximum number of serials to check for uniqueness in one batch
pub const MAX_SERIAL_BATCH_SIZE: usize = 10000;

/// P-256 curve order as BigUint
pub fn p256_order() -> BigUint {
    BigUint::parse_bytes(P256_ORDER_HEX.as_bytes(), 16).expect("valid hex")
}

/// P-384 curve order as BigUint
pub fn p384_order() -> BigUint {
    BigUint::parse_bytes(P384_ORDER_HEX.as_bytes(), 16).expect("valid hex")
}

/// BLS12-381 scalar field order as BigUint
pub fn bls12_381_order() -> BigUint {
    BigUint::parse_bytes(BLS12_381_ORDER_HEX.as_bytes(), 16).expect("valid hex")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_order_parsing() {
        let n256 = p256_order();
        assert!(n256 > BigUint::from(0u64));
        
        let n384 = p384_order();
        assert!(n384 > &n256);
    }

    #[test]
    fn test_hash_prefixes_non_empty() {
        assert!(!HASH_PREFIX_SAAC_PARAMS.is_empty());
        assert!(!HASH_PREFIX_SAAC_CRED.is_empty());
        assert!(!HASH_PREFIX_BIND_COMMIT.is_empty());
        assert!(!HASH_PREFIX_BIND_CHALLENGE.is_empty());
        assert!(!HASH_PREFIX_VRF_SERIAL.is_empty());
    }
}