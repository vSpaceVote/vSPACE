"""
TypedDict definitions for vSPACE anonymous credential data structures.

All types include JSON serialization support for MongoDB persistence
and augmented election record generation.

Citation: README.md#213-vspace-extension-feature-details
"""

from typing import Dict, List, Optional, TypedDict, Any


# =============================================================================
# F-100: SAAC Protocol Types
# =============================================================================


class SAACIssuerParams(TypedDict):
    """
    SAAC issuer public parameters for credential verification.

    Citation: README.md#f-100-saac-protocol-implementation

    Fields:
        curve: NIST curve identifier ("P-256" or "P-384")
        generator_g: Base point G (hex-encoded)
        generator_h: Independent base point H (hex-encoded)
        issuer_public_key: Issuer's public key Y (hex-encoded)
        parameter_hash: Hash of all parameters for integrity verification
    """

    curve: str
    generator_g: str
    generator_h: str
    issuer_public_key: str
    parameter_hash: str


class SAACCredential(TypedDict):
    """
    SAAC anonymous credential held by voter.

    Citation: README.md#f-100-saac-protocol-implementation

    Fields:
        credential_id: Unique identifier (unlinkable to issuance)
        blinded_commitment: Blinded credential commitment (hex-encoded)
        issuer_signature: Issuer's signature on blinded commitment (hex-encoded)
        auxiliary_info: Public auxiliary information (hex-encoded)
        expiration: ISO 8601 timestamp for credential validity
        election_binding: Optional election ID this credential is bound to
    """

    credential_id: str
    blinded_commitment: str
    issuer_signature: str
    auxiliary_info: str
    expiration: str
    election_binding: Optional[str]


class SAACPresentation(TypedDict):
    """
    SAAC credential presentation for ballot authentication.

    Citation: README.md#f-100-rq-002

    Fields:
        presentation_id: Unique presentation identifier
        credential_reference: Hash linking to credential (unlinkable)
        challenge_response: ZK proof response to challenge (hex-encoded)
        proof_of_knowledge: Schnorr-like ZK proof (hex-encoded)
        aux_info_commitment: Commitment to auxiliary info (hex-encoded)
        timestamp: ISO 8601 timestamp of presentation
    """

    presentation_id: str
    credential_reference: str
    challenge_response: str
    proof_of_knowledge: str
    aux_info_commitment: str
    timestamp: str


# =============================================================================
# F-101: Multi-Holder BBS Types
# =============================================================================


class MultiHolderShare(TypedDict):
    """
    Single credential share for one device.

    Citation: README.md#f-101-multi-holder-bbs-credentials

    Fields:
        share_id: Unique share identifier
        device_id: Device this share is stored on
        share_index: Index of this share in the threshold scheme (1..n)
        share_data: Encrypted share data (hex-encoded)
        share_proof: Proof that share is valid (hex-encoded)
        created_at: ISO 8601 timestamp of share creation
    """

    share_id: str
    device_id: str
    share_index: int
    share_data: str
    share_proof: str
    created_at: str


class MultiHolderCredential(TypedDict):
    """
    Multi-holder credential metadata (no secret data stored).

    Citation: README.md#f-101-rq-001

    Fields:
        credential_id: Unique identifier
        threshold: Number of shares required for presentation (t)
        total_shares: Total number of shares distributed (n)
        shares: List of share metadata (no secret data)
        curve: BLS12-381 curve identifier
        public_key: Public key for the credential (hex-encoded)
    """

    credential_id: str
    threshold: int
    total_shares: int
    shares: List[MultiHolderShare]
    curve: str
    public_key: str


# =============================================================================
# F-102: Credential-to-Ballot Binding Types
# =============================================================================


class BindingCommitment(TypedDict):
    """
    Pedersen commitment binding ballot nonce to credential serial.

    Citation: README.md#f-102-rq-001
    Mathematical: C = g^r * h^s where:
        r = ballot encryption nonce
        s = credential serial number

    Fields:
        commitment_id: Unique identifier
        commitment_value: Pedersen commitment C (hex-encoded)
        generator_g: Generator used for nonce (hex-encoded)
        generator_h: Generator used for serial (hex-encoded)
        ballot_reference: Hash reference to encrypted ballot
        election_id: Election this commitment belongs to
    """

    commitment_id: str
    commitment_value: str
    generator_g: str
    generator_h: str
    ballot_reference: str
    election_id: str


class BindingProof(TypedDict):
    """
    Zero-knowledge proof that commitment links ballot and credential.

    Citation: README.md#f-102-rq-002
    Protocol: Schnorr-like sigma protocol (Fiat-Shamir transformed)

    Fields:
        proof_id: Unique identifier
        commitment_reference: Hash linking to BindingCommitment
        challenge: Fiat-Shamir challenge (hex-encoded)
        response_r: Response for nonce r (hex-encoded)
        response_s: Response for serial s (hex-encoded)
        proof_hash: Hash of entire proof for integrity
    """

    proof_id: str
    commitment_reference: str
    challenge: str
    response_r: str
    response_s: str
    proof_hash: str


# =============================================================================
# F-103: One-Show Enforcement Types
# =============================================================================


class VRFSerialNumber(TypedDict):
    """
    VRF-derived serial number for one-show enforcement.

    Citation: README.md#f-103-rq-001
    Derivation: serial = VRF_sk(election_id)

    Fields:
        serial_id: Unique identifier
        serial_value: 256-bit serial number (hex-encoded)
        election_id: Election this serial belongs to
        vrf_proof: VRF proof of correct derivation (hex-encoded)
        credential_reference: Hash reference to credential (unlinkable)
        timestamp: ISO 8601 timestamp of derivation
        status: "unused" | "used" | "expired"
    """

    serial_id: str
    serial_value: str
    election_id: str
    vrf_proof: str
    credential_reference: str
    timestamp: str
    status: str


# =============================================================================
# F-109: Augmented Election Record Types
# =============================================================================


class VSPACERecordSection(TypedDict):
    """
    vSPACE extension section in augmented election record.

    Citation: README.md#f-109-augmented-election-record

    Fields:
        issuer_public_params: SAAC issuer parameters
        serial_numbers: List of all serial numbers (one per cast ballot)
        binding_commitments: List of all commitments (one per cast ballot)
        binding_proofs: List of all proofs (one per cast ballot)
        saac_aux_info: Public SAAC auxiliary information
    """

    issuer_public_params: SAACIssuerParams
    serial_numbers: List[VRFSerialNumber]
    binding_commitments: List[BindingCommitment]
    binding_proofs: List[BindingProof]
    saac_aux_info: str


class AugmentedElectionRecord(TypedDict):
    """
    Complete augmented election record with vSPACE extension.

    Citation: README.md#f-109-rq-001

    Fields:
        election_id: Election identifier
        standard_record: Standard ElectionGuard record (JSON)
        vspace_record: vSPACE extension section
        record_hash: Hash of complete record for integrity
        created_at: ISO 8601 timestamp of record creation
        version: vSPACE record version
    """

    election_id: str
    standard_record: Dict[str, Any]
    vspace_record: VSPACERecordSection
    record_hash: str
    created_at: str
    version: str
