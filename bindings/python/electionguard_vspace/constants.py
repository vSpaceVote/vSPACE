"""
Cryptographic constants for vSPACE anonymous credential operations.

All constants are derived from the technical specification in README.md
and aligned with ElectionGuard Specification 1.1.0 domain separation.

References:
- README.md#f-100-saac-protocol-implementation
- README.md#f-102-credential-to-ballot-binding
- README.md#f-103-one-show-enforcement
- ePrint 2025/513 (SAAC Protocol)
"""

# =============================================================================
# NIST P-256/P-384 Curve Parameters (SAAC Layer)
# =============================================================================

# NIST P-256 curve order (secp256r1)
# n = FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
P256_ORDER: int = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# NIST P-384 curve order (secp384r1)
# n = FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFF722F
P384_ORDER: int = (
    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFF722F
)

# =============================================================================
# Domain-Separated Hash Prefixes
# =============================================================================

# SAAC issuance hash prefix (prevents cross-context hash collisions)
# Citation: README.md#f-100-rq-001
HASH_PREFIX_SAAC_ISSUANCE: bytes = b"vSPACE_SAAC_ISSUANCE_V1\x00"

# SAAC presentation hash prefix
# Citation: README.md#f-100-rq-002
HASH_PREFIX_SAAC_PRESENTATION: bytes = b"vSPACE_SAAC_PRESENTATION_V1\x00"

# SAAC params hash prefix (for issuer parameters)
HASH_PREFIX_SAAC_PARAMS: bytes = b"vSPACE_SAAC_PARAMS_V1\x00"

# SAAC credential hash prefix
HASH_PREFIX_SAAC_CRED: bytes = b"vSPACE_SAAC_CRED_V1\x00"

# Credential-to-ballot binding commitment hash prefix
# Citation: README.md#f-102-rq-001
HASH_PREFIX_BINDING_COMMITMENT: bytes = b"vSPACE_BINDING_COMMITMENT_V1\x00"

# Binding challenge hash prefix (for Fiat-Shamir)
HASH_PREFIX_BINDING_CHALLENGE: bytes = b"vSPACE_BINDING_CHALLENGE_V1\x00"

# VRF serial number derivation hash prefix
# Citation: README.md#f-103-rq-001
HASH_PREFIX_VRF_SERIAL: bytes = b"vSPACE_VRF_SERIAL_V1\x00"

# =============================================================================
# Length Constants (bytes)
# =============================================================================

# SAAC auxiliary information length (public components)
# Citation: README.md#f-100-rq-003
SAAC_AUX_INFO_LENGTH: int = 64

# Serial number length (256-bit VRF output)
# Citation: README.md#f-103-rq-001
SERIAL_NUMBER_LENGTH: int = 32

# Binding commitment length (Pedersen commitment)
# Citation: README.md#f-102-rq-001
BINDING_COMMITMENT_LENGTH: int = 64

# Binding proof length (Fiat-Shamir sigma protocol)
# Citation: README.md#f-102-rq-002
BINDING_PROOF_LENGTH: int = 128

# =============================================================================
# Performance Targets (for benchmarking)
# =============================================================================

# SAAC presentation verification target: <50ms (C++)
SAAC_VERIFICATION_TARGET_MS: float = 50.0

# Serial number derivation target: <5ms
SERIAL_DERIVATION_TARGET_MS: float = 5.0

# Serial lookup target: <10ms
SERIAL_LOOKUP_TARGET_MS: float = 10.0

# Binding commitment generation target: <10ms
BINDING_COMMITMENT_TARGET_MS: float = 10.0

# Binding proof generation target: <50ms
BINDING_PROOF_TARGET_MS: float = 50.0

# =============================================================================
# Multi-Holder Threshold Configuration
# =============================================================================

# Minimum threshold: 1-of-2 (for accessibility)
MULTIHOLDER_MIN_THRESHOLD: int = 1
MULTIHOLDER_MIN_DEVICES: int = 2

# Maximum threshold: 2-of-2 (for high security)
MULTIHOLDER_MAX_THRESHOLD: int = 2
MULTIHOLDER_MAX_DEVICES: int = 2

# =============================================================================
# MongoDB Collection Names
# =============================================================================

VSPACE_CREDENTIALS_COLLECTION: str = "vspace_credentials"
VSPACE_SERIAL_NUMBERS_COLLECTION: str = "vspace_serial_numbers"
VSPACE_BINDINGS_COLLECTION: str = "vspace_bindings"
