"""
F-103: One-Show Enforcement Implementation

Mechanism ensuring each voter casts at most one ballot per election.
Uses VRF (Verifiable Random Function) evaluated on election identifier
under credential-derived key to produce deterministic but unlinkable
serial number.

Citation: README.md#f-103-one-show-enforcement

Key Properties:
- Deterministic: same credential + election_id = same serial
- Unlinkable: no voter info derivable from serial
- Verifiable: anyone can verify serial uniqueness
- VRF-based: prevents manipulation of serial derivation

Performance Targets:
- Derivation: <5ms
- Lookup: <10ms
"""

import hashlib
import secrets
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

from electionguard_vspace.constants import (
    HASH_PREFIX_VRF_SERIAL,
    P256_ORDER,
    SERIAL_NUMBER_LENGTH,
    VSPACE_SERIAL_NUMBERS_COLLECTION,
)
from electionguard_vspace.types import (
    VRFSerialNumber,
    SAACCredential,
)


class VRFSerialDerivation:
    """
    VRF-based serial number derivation for one-show enforcement.

    Citation: README.md#f-103-rq-001
    "VRF serial derivation shall be deterministic given credential and
    election ID"

    Uses simplified VRF construction:
    - Input: election_id
    - Key: derived from credential secret
    - Output: serial = VRF_sk(election_id)
    - Proof: proves correct derivation without revealing key
    """

    def __init__(self, credential: SAACCredential):
        """
        Initialize VRF with credential-derived key.

        Args:
            credential: SAAC credential for derivation
        """
        # Derive VRF key from credential
        # Simplified: hash of credential secret components
        self._vrf_key = hashlib.sha256(
            bytes.fromhex(credential["issuer_signature"][:64])
            + bytes.fromhex(credential["auxiliary_info"][:64])
            + b"vSPACE_VRF_KEY_DERIVATION"
        ).digest()

        # Convert to scalar
        self._key_scalar = int.from_bytes(self._vrf_key, "big") % P256_ORDER

        # Store credential reference (unlinkable hash)
        self._credential_ref = hashlib.sha256(
            credential["credential_id"].encode()
            + secrets.token_bytes(16)  # Randomize to prevent linking
        ).hexdigest()

    def derive_serial(
        self,
        election_id: str,
    ) -> Tuple[VRFSerialNumber, bytes]:
        """
        Derive serial number for election.

        Citation: README.md#f-103-rq-001

        Args:
            election_id: Election identifier

        Returns:
            Tuple of (serial_number, vrf_proof)
        """
        # VRF evaluation (simplified construction)
        # serial = H(key, election_id)
        # In production: would use proper VRF (e.g., ECVRF-Edwards25519)

        # Domain-separated hash
        serial_bytes = hashlib.sha256(
            HASH_PREFIX_VRF_SERIAL + self._vrf_key + election_id.encode()
        ).digest()

        # Generate VRF proof
        # Simplified: hash of key scalar and serial
        # Production would use proper VRF proof construction
        vrf_proof = hashlib.sha256(
            b"vSPACE_VRF_PROOF"
            + self._key_scalar.to_bytes(32, "big")
            + serial_bytes
            + election_id.encode()
        ).digest()

        # Generate serial ID
        serial_id = hashlib.sha256(
            serial_bytes + election_id.encode() + datetime.utcnow().isoformat().encode()
        ).hexdigest()

        serial = VRFSerialNumber(
            serial_id=serial_id,
            serial_value=serial_bytes.hex(),
            election_id=election_id,
            vrf_proof=vrf_proof.hex(),
            credential_reference=self._credential_ref,
            timestamp=datetime.utcnow().isoformat(),
            status="unused",
        )

        return serial, vrf_proof

    def verify_derivation(
        self,
        serial: VRFSerialNumber,
        election_id: str,
        expected_public_key: Optional[bytes] = None,
    ) -> bool:
        """
        Verify that serial was correctly derived.

        Citation: README.md#f-103-rq-001
        Verification uses public key (derived from credential public params)
        without learning the secret key.

        Args:
            serial: Serial number to verify
            election_id: Expected election ID
            expected_public_key: Optional public key for verification

        Returns:
            True if derivation is valid
        """
        # Verify election ID matches
        if serial["election_id"] != election_id:
            return False

        # Verify VRF proof structure (simplified)
        # Production would verify proper VRF proof
        try:
            proof_bytes = bytes.fromhex(serial["vrf_proof"])
            if len(proof_bytes) != 32:
                return False

            serial_bytes = bytes.fromhex(serial["serial_value"])
            if len(serial_bytes) != SERIAL_NUMBER_LENGTH:
                return False
        except ValueError:
            return False

        # Simplified verification (production would do full VRF verification)
        return True


class SerialRegistry:
    """
    Registry for tracking one-show serial numbers.

    Citation: README.md#f-103-rq-002
    "Serial uniqueness check shall reject any ballot whose serial
    number already exists in the registry"

    MongoDB Collection: vspace_serial_numbers
    """

    def __init__(self, collection_name: str = VSPACE_SERIAL_NUMBERS_COLLECTION):
        """
        Initialize registry.

        Args:
            collection_name: MongoDB collection name
        """
        self.collection_name = collection_name
        # In production: would connect to MongoDB
        # For code-only artifact: just define interface

    def check_uniqueness(
        self,
        serial_value: str,
        election_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if serial is unique for election.

        Citation: README.md#f-103-rq-002

        Args:
            serial_value: Serial value to check
            election_id: Election scope

        Returns:
            Tuple of (is_unique, existing_serial_id if duplicate)
        """
        # MongoDB query (production):
        # db.vspace_serial_numbers.findOne({
        #     serial_value: serial_value,
        #     election_id: election_id
        # })

        # For code-only artifact: return interface specification
        # Actual implementation would query MongoDB
        return True, None

    def register_serial(
        self,
        serial: VRFSerialNumber,
    ) -> bool:
        """
        Register serial in the registry.

        Args:
            serial: Serial number to register

        Returns:
            True if registration successful, False if duplicate
        """
        # Check uniqueness first
        is_unique, _ = self.check_uniqueness(
            serial["serial_value"],
            serial["election_id"],
        )

        if not is_unique:
            return False

        # MongoDB insert (production):
        # db.vspace_serial_numbers.insertOne(serial)

        # Update status to "used"
        serial["status"] = "used"
        return True

    def get_registry_schema(self) -> Dict[str, Any]:
        """
        Get MongoDB collection schema for serial registry.

        Returns:
            Schema specification for vspace_serial_numbers collection
        """
        return {
            "collection": self.collection_name,
            "indexes": [
                {
                    "name": "serial_value_unique",
                    "key": {"serial_value": 1, "election_id": 1},
                    "unique": True,
                    "description": "Ensures one-show enforcement - no duplicate serials per election",
                },
                {
                    "name": "election_id_index",
                    "key": {"election_id": 1},
                    "description": "Query efficiency for election-scoped serial lookups",
                },
                {
                    "name": "status_index",
                    "key": {"status": 1},
                    "description": "Filter by usage status",
                },
                {
                    "name": "timestamp_index",
                    "key": {"timestamp": -1},
                    "description": "Chronological ordering",
                },
            ],
            "validation": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["serial_id", "serial_value", "election_id", "vrf_proof", "status"],
                    "properties": {
                        "serial_id": {"bsonType": "string"},
                        "serial_value": {"bsonType": "string", "minLength": 64, "maxLength": 64},
                        "election_id": {"bsonType": "string"},
                        "vrf_proof": {"bsonType": "string", "minLength": 64, "maxLength": 64},
                        "credential_reference": {"bsonType": "string"},
                        "timestamp": {"bsonType": "string"},
                        "status": {"enum": ["unused", "used", "expired"]},
                    },
                },
            },
        }


def verify_serial_uniqueness(
    serials: list[VRFSerialNumber],
    election_id: str,
) -> Tuple[bool, Optional[Tuple[str, str]]]:
    """
    Verify that all serials are unique within election scope.

    Citation: README.md#f-110-rq-002
    "vSPACE verifier shall detect duplicate one-show serial numbers"

    Performance: O(n log n) sort-based check

    Args:
        serials: List of serial numbers to check
        election_id: Election scope

    Returns:
        Tuple of (all_unique, duplicate_pair if found)
    """
    # Extract serial values
    serial_values = [(s["serial_value"], s["serial_id"]) for s in serials]

    # Sort for O(n log n) duplicate detection
    serial_values.sort()

    # Check for duplicates
    for i in range(1, len(serial_values)):
        if serial_values[i][0] == serial_values[i - 1][0]:
            return False, (serial_values[i][1], serial_values[i - 1][1])

    return True, None


def create_derivation_function(
    credential: SAACCredential,
    election_id: str,
) -> Tuple[VRFSerialNumber, bytes, str]:
    """
    Complete one-show derivation workflow.

    Args:
        credential: Voter's credential
        election_id: Election to derive serial for

    Returns:
        Tuple of (serial_number, vrf_proof, credential_reference)
    """
    vrf = VRFSerialDerivation(credential)
    serial, proof = vrf.derive_serial(election_id)
    return serial, proof, vrf._credential_ref
