//! Error types for vSPACE verification.

use thiserror::Error;

/// vSPACE verification error types
#[derive(Debug, Error)]
pub enum VSpaceError {
    /// Invalid cryptographic parameter
    #[error("Invalid parameter: {0}")]
    InvalidParameter(String),
    
    /// Invalid curve point encoding
    #[error("Invalid point encoding: {0}")]
    InvalidPointEncoding(String),
    
    /// Curve operation failed
    #[error("Curve operation failed: {0}")]
    CurveOperationFailed(String),
    
    /// Proof verification failed
    #[error("Proof verification failed: {0}")]
    ProofVerificationFailed(String),
    
    /// Invalid signature
    #[error("Invalid signature: {0}")]
    InvalidSignature(String),
    
    /// Serial number already used (one-show violation)
    #[error("Serial number already used: {0}")]
    SerialAlreadyUsed(String),
    
    /// Duplicate serial detected
    #[error("Duplicate serial detected: {0}")]
    DuplicateSerial(String),
    
    /// Invalid hash
    #[error("Invalid hash: {0}")]
    InvalidHash(String),
    
    /// Serialization error
    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),
    
    /// Hex decoding error
    #[error("Hex decoding error: {0}")]
    HexDecodingError(String),
    
    /// Missing required field
    #[error("Missing required field: {0}")]
    MissingField(String),
    
    /// Unsupported curve
    #[error("Unsupported curve: {0}")]
    UnsupportedCurve(String),
    
    /// Verification failed
    #[error("Verification failed: {0}")]
    VerificationFailed(String),
    
    /// Batch verification error
    #[error("Batch verification failed: {0} errors out of {1} items")]
    BatchVerificationFailed(usize, usize),
}

/// Result type for vSPACE operations
pub type VSpaceResult<T> = Result<T, VSpaceError>;