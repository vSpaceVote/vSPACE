"""
vSPACE: Anonymous Credential Extensions for ElectionGuard

This package implements the vSPACE extension layer for ElectionGuard,
providing anonymous credential authentication, credential-to-ballot binding,
one-show enforcement, and augmented election record capabilities.

Key Features:
- F-100: SAAC Protocol Implementation (Server-Aided Anonymous Credentials)
- F-101: Multi-Holder BBS Credentials
- F-102: Credential-to-Ballot Binding
- F-103: One-Show Enforcement
- F-109: Augmented Election Record

This is pre-release software and should NOT be used for production elections.
See README.md for full technical specification and constraints.

License: MIT
Repository: https://github.com/vSpaceVote/vSPACE
"""

from electionguard_vspace.constants import (
    P256_ORDER,
    P384_ORDER,
    HASH_PREFIX_SAAC_ISSUANCE,
    HASH_PREFIX_SAAC_PRESENTATION,
    HASH_PREFIX_BINDING_COMMITMENT,
    HASH_PREFIX_VRF_SERIAL,
    SAAC_AUX_INFO_LENGTH,
    SERIAL_NUMBER_LENGTH,
    BINDING_COMMITMENT_LENGTH,
)

from electionguard_vspace.types import (
    SAACIssuerParams,
    SAACCredential,
    SAACPresentation,
    MultiHolderShare,
    MultiHolderCredential,
    BindingCommitment,
    BindingProof,
    VRFSerialNumber,
    AugmentedElectionRecord,
)

__version__ = "0.1.0"
__author__ = "vSPACE Team"
__license__ = "MIT"

__all__ = [
    # Constants
    "P256_ORDER",
    "P384_ORDER",
    "HASH_PREFIX_SAAC_ISSUANCE",
    "HASH_PREFIX_SAAC_PRESENTATION",
    "HASH_PREFIX_BINDING_COMMITMENT",
    "HASH_PREFIX_VRF_SERIAL",
    "SAAC_AUX_INFO_LENGTH",
    "SERIAL_NUMBER_LENGTH",
    "BINDING_COMMITMENT_LENGTH",
    # Types
    "SAACIssuerParams",
    "SAACCredential",
    "SAACPresentation",
    "MultiHolderShare",
    "MultiHolderCredential",
    "BindingCommitment",
    "BindingProof",
    "VRFSerialNumber",
    "AugmentedElectionRecord",
]
