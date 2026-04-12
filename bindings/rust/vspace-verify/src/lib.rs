//! # vSPACE Verifier Extension
//!
//! Anonymous credential verification primitives for ElectionGuard.
//!
//! ## Features
//!
//! - **F-100**: SAAC Protocol verification (NIST P-256/P-384)
//! - **F-102**: Credential-to-Ballot binding proof verification
//! - **F-103**: One-show serial uniqueness verification
//!
//! ## Usage
//!
//! ```rust,ignore
//! use vspace_verify::{saac::verify_presentation, binding::verify_binding_proof};
//!
//! // Verify SAAC presentation
//! let valid = verify_presentation(&presentation, &issuer_params)?;
//!
//! // Verify binding proof
//! let valid = verify_binding_proof(&proof, &commitment)?;
//! ```

#![forbid(unsafe_code)]
#![warn(missing_docs)]
#![warn(rustdoc::missing_crate_level_docs)]

pub mod constants;
pub mod types;
pub mod errors;

#[cfg(feature = "saac")]
pub mod saac;

#[cfg(feature = "binding")]
pub mod binding;

#[cfg(feature = "serial")]
pub mod serial;

pub use errors::{VSpaceError, VSpaceResult};
pub use types::*;

/// Crate version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// vSPACE specification version this implementation targets
pub const SPEC_VERSION: &str = "0.1.0-pre";