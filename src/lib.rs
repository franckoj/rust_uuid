use pyo3::prelude::*;
use uuid::Uuid;
use std::sync::OnceLock;

// Predefined namespace UUIDs (matching Python's uuid module)
const NAMESPACE_DNS_UUID: Uuid = uuid::uuid!("6ba7b810-9dad-11d1-80b4-00c04fd430c8");
const NAMESPACE_URL_UUID: Uuid = uuid::uuid!("6ba7b811-9dad-11d1-80b4-00c04fd430c8");
const NAMESPACE_OID_UUID: Uuid = uuid::uuid!("6ba7b812-9dad-11d1-80b4-00c04fd430c8");
const NAMESPACE_X500_UUID: Uuid = uuid::uuid!("6ba7b814-9dad-11d1-80b4-00c04fd430c8");

// Static node ID for uuid1 - initialize once
static NODE_ID: OnceLock<[u8; 6]> = OnceLock::new();

/// Generate a version 1 UUID (time-based)
#[pyfunction]
fn uuid1() -> String {
    // Initialize node ID once (simulate MAC address)
    let node_id = NODE_ID.get_or_init(|| {
        use std::hash::{Hash, Hasher};
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        std::process::id().hash(&mut hasher);
        let hash = hasher.finish();
        [
            (hash & 0xff) as u8,
            ((hash >> 8) & 0xff) as u8,
            ((hash >> 16) & 0xff) as u8,
            ((hash >> 24) & 0xff) as u8,
            ((hash >> 32) & 0xff) as u8,
            ((hash >> 40) & 0xff) as u8 | 0x01, // Set multicast bit
        ]
    });
    
    let uuid = Uuid::now_v1(node_id);
    format_uuid_fast(&uuid)
}

/// Generate a version 3 UUID (MD5 hash-based)
#[pyfunction]
fn uuid3(namespace: &str, name: &str) -> PyResult<String> {
    let namespace_uuid = parse_namespace(namespace)?;
    let uuid = Uuid::new_v3(&namespace_uuid, name.as_bytes());
    Ok(format_uuid_fast(&uuid))
}

/// Generate a version 4 UUID (random)
#[pyfunction]
fn uuid4() -> String {
    let uuid = Uuid::new_v4();
    format_uuid_fast(&uuid)
}

/// Generate a version 5 UUID (SHA1 hash-based)
#[pyfunction]
fn uuid5(namespace: &str, name: &str) -> PyResult<String> {
    let namespace_uuid = parse_namespace(namespace)?;
    let uuid = Uuid::new_v5(&namespace_uuid, name.as_bytes());
    Ok(format_uuid_fast(&uuid))
}

/// Generate multiple version 4 UUIDs at once (batch operation)
#[pyfunction]
fn uuid4_batch(count: usize) -> Vec<String> {
    (0..count).map(|_| {
        let uuid = Uuid::new_v4();
        format_uuid_fast(&uuid)
    }).collect()
}

/// Fast UUID formatting without allocation overhead
#[inline]
fn format_uuid_fast(uuid: &Uuid) -> String {
    uuid.as_hyphenated().to_string()
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

/// Optimized UUID class that holds the UUID in binary format
#[pyclass]
struct FastUUID {
    uuid: Uuid,
}

#[pymethods]
impl FastUUID {
    #[new]
    fn new(uuid_str: Option<&str>) -> PyResult<Self> {
        let uuid = match uuid_str {
            Some(s) => Uuid::parse_str(s)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid UUID: {}", e)))?,
            None => Uuid::new_v4(),
        };
        Ok(FastUUID { uuid })
    }
    
    fn __str__(&self) -> String {
        format_uuid_fast(&self.uuid)
    }
    
    fn __repr__(&self) -> String {
        format!("FastUUID('{}')", self.__str__())
    }
    
    #[getter]
    fn hex(&self) -> String {
        self.uuid.as_simple().to_string()
    }
    
    #[getter]
    fn bytes(&self) -> Vec<u8> {
        self.uuid.as_bytes().to_vec()
    }
    
    #[getter]
    fn version(&self) -> usize {
        self.uuid.get_version_num()
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
    m.add_function(wrap_pyfunction!(uuid4_batch, m)?)?;
    
    // Add FastUUID class
    m.add_class::<FastUUID>()?;
    
    // Add namespace constants
    m.add("NAMESPACE_DNS", NAMESPACE_DNS_UUID.to_string())?;
    m.add("NAMESPACE_URL", NAMESPACE_URL_UUID.to_string())?;
    m.add("NAMESPACE_OID", NAMESPACE_OID_UUID.to_string())?;
    m.add("NAMESPACE_X500", NAMESPACE_X500_UUID.to_string())?;
    
    Ok(())
}