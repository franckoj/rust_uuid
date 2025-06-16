use pyo3::prelude::*;
use uuid::Uuid;
use std::time::{SystemTime, UNIX_EPOCH};

// Predefined namespace UUIDs (matching Python's uuid module)
const NAMESPACE_DNS_UUID: Uuid = uuid::uuid!("6ba7b810-9dad-11d1-80b4-00c04fd430c8");
const NAMESPACE_URL_UUID: Uuid = uuid::uuid!("6ba7b811-9dad-11d1-80b4-00c04fd430c8");
const NAMESPACE_OID_UUID: Uuid = uuid::uuid!("6ba7b812-9dad-11d1-80b4-00c04fd430c8");
const NAMESPACE_X500_UUID: Uuid = uuid::uuid!("6ba7b814-9dad-11d1-80b4-00c04fd430c8");

/// Generate a version 1 UUID (time-based)
#[pyfunction]
fn uuid1() -> PyResult<String> {
    // Get current timestamp
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Time error: {}", e)))?;
    
    // Convert to UUID timestamp (100-nanosecond intervals since UUID epoch)
    let uuid_epoch_offset = 122192928000000000u64; // Difference between Unix epoch and UUID epoch
    let timestamp = (now.as_nanos() as u64 / 100) + uuid_epoch_offset;
    
    // Generate a simple node ID based on timestamp (in real implementation, you'd use MAC address)
    let node_id = [
        (timestamp & 0xff) as u8,
        ((timestamp >> 8) & 0xff) as u8,
        ((timestamp >> 16) & 0xff) as u8,
        ((timestamp >> 24) & 0xff) as u8,
        ((timestamp >> 32) & 0xff) as u8,
        ((timestamp >> 40) & 0xff) as u8,
    ];
    
    let uuid = Uuid::now_v1(&node_id);
    Ok(uuid.to_string())
}

/// Generate a version 3 UUID (MD5 hash-based)
#[pyfunction]
fn uuid3(namespace: &str, name: &str) -> PyResult<String> {
    let namespace_uuid = parse_namespace(namespace)?;
    let uuid = Uuid::new_v3(&namespace_uuid, name.as_bytes());
    Ok(uuid.to_string())
}

/// Generate a version 4 UUID (random)
#[pyfunction]
fn uuid4() -> PyResult<String> {
    let uuid = Uuid::new_v4();
    Ok(uuid.to_string())
}

/// Generate a version 5 UUID (SHA1 hash-based)
#[pyfunction]
fn uuid5(namespace: &str, name: &str) -> PyResult<String> {
    let namespace_uuid = parse_namespace(namespace)?;
    let uuid = Uuid::new_v5(&namespace_uuid, name.as_bytes());
    Ok(uuid.to_string())
}

/// Helper function to parse namespace string or use predefined namespaces
fn parse_namespace(namespace: &str) -> PyResult<Uuid> {
    match namespace {
        "NAMESPACE_DNS" => Ok(NAMESPACE_DNS_UUID),
        "NAMESPACE_URL" => Ok(NAMESPACE_URL_UUID),
        "NAMESPACE_OID" => Ok(NAMESPACE_OID_UUID),
        "NAMESPACE_X500" => Ok(NAMESPACE_X500_UUID),
        _ => {
            // Try to parse as UUID string
            Uuid::parse_str(namespace)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid namespace UUID: {}", e)))
        }
    }
}

/// Python module definition
#[pymodule]
fn rust_uuid(_py: Python, m: &PyModule) -> PyResult<()> {
    // Add functions
    m.add_function(wrap_pyfunction!(uuid1, m)?)?;
    m.add_function(wrap_pyfunction!(uuid3, m)?)?;
    m.add_function(wrap_pyfunction!(uuid4, m)?)?;
    m.add_function(wrap_pyfunction!(uuid5, m)?)?;
    
    // Add namespace constants
    m.add("NAMESPACE_DNS", NAMESPACE_DNS_UUID.to_string())?;
    m.add("NAMESPACE_URL", NAMESPACE_URL_UUID.to_string())?;
    m.add("NAMESPACE_OID", NAMESPACE_OID_UUID.to_string())?;
    m.add("NAMESPACE_X500", NAMESPACE_X500_UUID.to_string())?;
    
    Ok(())
}