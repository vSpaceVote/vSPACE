"""
F-102: Credential-to-Ballot Binding Implementation

Cryptographic binding of anonymous credential presentation to
ElectionGuard ballot encryption using Pedersen commitments and
Schnorr-like sigma protocols (Fiat-Shamir transformed).

Citation: README.md#f-102-credential-to-ballot-binding

Mathematical Foundation:
- Commitment: C = g^r * h^s
  where r = ballot encryption nonce, s = credential serial number
- Proof: Zero-knowledge proof that C commits to both r and s
  without revealing either value

Key Properties:
- Ballot stuffing prevention: each ballot requires valid credential
- Unlinkability: no voter-to-ballot correlation
- Ballot secrecy preservation: ElectionGuard encryption unaffected

Performance Targets:
- Commitment generation: <10ms
- Proof generation: <50ms
"""

import hashlib
import secrets
from typing import Tuple, Optional
from datetime import datetime

from electionguard_vspace.constants import (
    HASH_PREFIX_BINDING_COMMITMENT,
    P256_ORDER,
    BINDING_COMMITMENT_LENGTH,
    BINDING_PROOF_LENGTH,
)
from electionguard_vspace.types import (
    BindingCommitment,
    BindingProof,
    SAACCredential,
    SAACPresentation,
)


class BindingGenerator:
    """
    Generates Pedersen commitment binding ballot nonce to credential serial.

    Citation: README.md#f-102-rq-001
    "Pedersen commitment shall correctly bind ballot encryption nonce r
    to credential serial number s"

    The commitment C = g^r * h^s is computationally binding under the
    discrete log assumption, ensuring each ballot is linked to exactly
    one credential without revealing the link.
    """

    def __init__(self, generator_g: bytes, generator_h: bytes):
        """
        Initialize binding generator with Pedersen generators.

        Args:
            generator_g: Generator for ballot nonce component
            generator_h: Generator for credential serial component
        """
        self._g_scalar = int.from_bytes(generator_g, "big") % P256_ORDER
        self._h_scalar = int.from_bytes(generator_h, "big") % P256_ORDER

    def generate_commitment(
        self,
        ballot_nonce: bytes,
        credential_serial: bytes,
        election_id: str,
        ballot_reference: str,
    ) -> Tuple[BindingCommitment, int, int]:
        """
        Generate Pedersen commitment C = g^r * h^s.

        Citation: README.md#f-102-rq-001

        Args:
            ballot_nonce: Ballot encryption nonce (r)
            credential_serial: Credential serial number (s)
            election_id: Election identifier
            ballot_reference: Hash reference to encrypted ballot

        Returns:
            Tuple of (commitment, r_scalar, s_scalar)
            r_scalar and s_scalar are needed for proof generation
        """
        # Convert inputs to scalars
        r_scalar = int.from_bytes(ballot_nonce, "big") % P256_ORDER
        s_scalar = int.from_bytes(credential_serial, "big") % P256_ORDER

        # Compute commitment: C = g^r * h^s (mod P256_ORDER)
        # Simplified: in production, this would be curve point multiplication
        commitment_value = (
            pow(self._g_scalar, r_scalar, P256_ORDER) * pow(self._h_scalar, s_scalar, P256_ORDER)
        ) % P256_ORDER

        # Encode commitment
        commitment_bytes = commitment_value.to_bytes(BINDING_COMMITMENT_LENGTH // 2, "big")

        # Generate commitment ID
        commitment_id = hashlib.sha256(
            HASH_PREFIX_BINDING_COMMITMENT
            + commitment_bytes
            + election_id.encode()
            + ballot_reference.encode()
        ).hexdigest()

        commitment = BindingCommitment(
            commitment_id=commitment_id,
            commitment_value=commitment_bytes.hex(),
            generator_g=self._g_scalar.to_bytes(32, "big").hex(),
            generator_h=self._h_scalar.to_bytes(32, "big").hex(),
            ballot_reference=ballot_reference,
            election_id=election_id,
        )

        return commitment, r_scalar, s_scalar


class ProofGenerator:
    """
    Generates zero-knowledge binding proof.

    Citation: README.md#f-102-rq-002
    "Zero-knowledge binding proof shall demonstrate commitment links
    to both ballot and credential without revealing either"

    Uses Schnorr-like sigma protocol with Fiat-Shamir transformation:
    1. Prover picks random w1, w2
    2. Computes A = g^w1 * h^w2
    3. Challenge c = H(g, h, C, A, election_id)
    4. Responses: z1 = w1 + c*r, z2 = w2 + c*s
    5. Proof: (c, z1, z2)
    """

    def __init__(self, generator_g: int, generator_h: int):
        """
        Initialize proof generator.

        Args:
            generator_g: Generator g as scalar
            generator_h: Generator h as scalar
        """
        self._g = generator_g
        self._h = generator_h

    def generate_proof(
        self,
        commitment: BindingCommitment,
        r_scalar: int,
        s_scalar: int,
    ) -> BindingProof:
        """
        Generate ZK proof that C commits to (r, s).

        Citation: README.md#f-102-rq-002

        Args:
            commitment: The Pedersen commitment
            r_scalar: Ballot nonce value
            s_scalar: Credential serial value

        Returns:
            Binding proof (c, z1, z2)
        """
        # Step 1: Pick random witnesses w1, w2
        w1 = secrets.randbelow(P256_ORDER)
        w2 = secrets.randbelow(P256_ORDER)

        # Step 2: Compute announcement A = g^w1 * h^w2
        A = (pow(self._g, w1, P256_ORDER) * pow(self._h, w2, P256_ORDER)) % P256_ORDER

        # Step 3: Fiat-Shamir challenge
        # c = H(g, h, C, A, election_id)
        challenge_bytes = hashlib.sha256(
            self._g.to_bytes(32, "big")
            + self._h.to_bytes(32, "big")
            + bytes.fromhex(commitment["commitment_value"])
            + A.to_bytes(32, "big")
            + commitment["election_id"].encode()
        ).digest()
        challenge = int.from_bytes(challenge_bytes, "big") % P256_ORDER

        # Step 4: Compute responses
        # z1 = w1 + c * r (mod order)
        # z2 = w2 + c * s (mod order)
        z1 = (w1 + challenge * r_scalar) % P256_ORDER
        z2 = (w2 + challenge * s_scalar) % P256_ORDER

        # Generate proof ID
        proof_id = hashlib.sha256(
            commitment["commitment_id"].encode()
            + challenge_bytes
            + z1.to_bytes(32, "big")
            + z2.to_bytes(32, "big")
        ).hexdigest()

        # Compute proof hash for integrity
        proof_hash = hashlib.sha256(
            commitment["commitment_id"].encode()
            + challenge_bytes
            + z1.to_bytes(32, "big")
            + z2.to_bytes(32, "big")
        ).hexdigest()

        return BindingProof(
            proof_id=proof_id,
            commitment_reference=commitment["commitment_id"],
            challenge=challenge.to_bytes(32, "big").hex(),
            response_r=z1.to_bytes(32, "big").hex(),
            response_s=z2.to_bytes(32, "big").hex(),
            proof_hash=proof_hash,
        )


def verify_binding_proof(
    commitment: BindingCommitment,
    proof: BindingProof,
) -> bool:
    """
    Verify that binding proof is valid for commitment.

    Citation: README.md#f-102-rq-002
    "Proof passes verification; extraction of r or s from proof is
    computationally infeasible"

    Verification:
    1. Parse c, z1, z2 from proof
    2. Compute A' = g^z1 * h^z2 * C^{-c}
    3. Compute c' = H(g, h, C, A', election_id)
    4. Verify c == c'

    Args:
        commitment: The Pedersen commitment
        proof: The binding proof

    Returns:
        True if proof is valid, False otherwise

    Performance Target: <50ms
    """
    try:
        # Parse values using proper hex decoding
        g = int.from_bytes(bytes.fromhex(commitment["generator_g"]), "big") % P256_ORDER
        h = int.from_bytes(bytes.fromhex(commitment["generator_h"]), "big") % P256_ORDER
        C = int.from_bytes(bytes.fromhex(commitment["commitment_value"]), "big") % P256_ORDER
        c = int.from_bytes(bytes.fromhex(proof["challenge"]), "big") % P256_ORDER
        z1 = int.from_bytes(bytes.fromhex(proof["response_r"]), "big") % P256_ORDER
        z2 = int.from_bytes(bytes.fromhex(proof["response_s"]), "big") % P256_ORDER
    except (ValueError, TypeError):
        return False

    # Compute A' = g^z1 * h^z2 * C^{-c}
    # Using Fermat's little theorem: C^{-c} = C^{order-c} mod order
    C_neg_c = pow(C, P256_ORDER - c, P256_ORDER)
    A_prime = (pow(g, z1, P256_ORDER) * pow(h, z2, P256_ORDER) * C_neg_c) % P256_ORDER

    # Recompute challenge
    challenge_prime_bytes = hashlib.sha256(
        g.to_bytes(32, "big")
        + h.to_bytes(32, "big")
        + bytes.fromhex(commitment["commitment_value"])
        + A_prime.to_bytes(32, "big")
        + commitment["election_id"].encode()
    ).digest()
    c_prime = int.from_bytes(challenge_prime_bytes, "big") % P256_ORDER

    # Verify challenge matches
    return c == c_prime


def wrap_ballot_encryption(
    ballot_nonce: bytes,
    credential_serial: bytes,
    election_id: str,
    ballot_reference: str,
    presentation: SAACPresentation,
) -> Tuple[BindingCommitment, BindingProof]:
    """
    Wrap ElectionGuard ballot encryption with credential binding.

    Citation: README.md#f-102-rq-003
    "Binding layer shall wrap electionguard.encrypt without modifying
    its internal behaviour"

    This function is additive - it does not modify the ElectionGuard
    encryption process. It creates binding artifacts that are appended
    to the election record.

    Args:
        ballot_nonce: Nonce from ElectionGuard encryption
        credential_serial: Serial from credential presentation
        election_id: Election identifier
        ballot_reference: Reference to encrypted ballot
        presentation: SAAC presentation used

    Returns:
        Tuple of (binding_commitment, binding_proof)
    """
    # Generate generators (from election context in production)
    # Simplified: use deterministic derivation
    generator_g_bytes = hashlib.sha256(b"vSPACE_BINDING_G" + election_id.encode()).digest()
    generator_h_bytes = hashlib.sha256(b"vSPACE_BINDING_H" + election_id.encode()).digest()

    # Generate commitment
    binding_gen = BindingGenerator(generator_g_bytes, generator_h_bytes)
    commitment, r_scalar, s_scalar = binding_gen.generate_commitment(
        ballot_nonce,
        credential_serial,
        election_id,
        ballot_reference,
    )

    # Generate proof
    g_scalar = int.from_bytes(generator_g_bytes, "big") % P256_ORDER
    h_scalar = int.from_bytes(generator_h_bytes, "big") % P256_ORDER
    proof_gen = ProofGenerator(g_scalar, h_scalar)
    proof = proof_gen.generate_proof(commitment, r_scalar, s_scalar)

    return commitment, proof


# Helper function for hex parsing
def int_from_hex(hex_str: str, byteorder: str) -> int:
    """Convert hex string to integer."""
    return int.from_bytes(bytes.fromhex(hex_str), byteorder)
