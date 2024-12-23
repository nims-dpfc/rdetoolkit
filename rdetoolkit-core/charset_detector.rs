use chardetng::EncodingDetector;
use pyo3::exceptions::{PyIOError, PyUnicodeDecodeError};
use pyo3::prelude::*;
use std::fs::File;
use std::io::Read;

#[pyfunction]
pub fn read_file_with_encoding(file_path: &str) -> PyResult<String> {
    let mut file = File::open(file_path)?;
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes)?;

    let mut detector = EncodingDetector::new();
    detector.feed(&bytes, true);
    let encoding = detector.guess(None, true);
    let (content, _, had_errors) = encoding.decode(&bytes);

    if had_errors {
        println!("Warning: Some characters could not be decoded correctly");
    }

    Ok(content.into_owned())
}

#[pyfunction]
pub fn detect_encoding(path: &str) -> PyResult<String> {
    if !std::path::Path::new(path).exists() {
        return Err(PyIOError::new_err(format!("File not found: {}", path)));
    }
    let mut file = File::open(path)?;

    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes)
        .map_err(|e| PyIOError::new_err(format!("Failed to read file: {}", e)))?;

    let mut detector = EncodingDetector::new();
    detector.feed(&bytes, true);
    let encoding = detector.guess(None, true);

    let encoding_name = encoding.name();
    if encoding_name.is_empty() {
        return Err(PyUnicodeDecodeError::new_err("No valid encoding detected"));
    }
    Ok(encoding_name.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    use pyo3::prelude::*;
    use std::fs::File;
    use std::io::Write;
    use tempfile::tempdir;

    #[test]
    fn test_read_utf8_file() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("utf-8");

        let mut file = File::create(&file_path).unwrap();
        let content = "こんにちは、rdetoolkit_core!";
        file.write_all(content.as_bytes()).unwrap();

        let result = read_file_with_encoding(file_path.to_str().unwrap());
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), content);
    }

    #[test]
    fn test_read_shitf_jis_file() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("shift_jis.txt");

        let mut file = File::create(&file_path).unwrap();
        let content_shift_jis = vec![0x82, 0xB1, 0x82, 0xF1, 0x82, 0xC9, 0x82, 0xBF, 0x82, 0xCD];
        file.write_all(&content_shift_jis).unwrap();

        let result = read_file_with_encoding(file_path.to_str().unwrap());
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), "こんにちは");
    }

    #[test]
    fn test_decoding_errors() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("invalid.txt");

        let mut file = File::create(&file_path).unwrap();
        let invalid_bytes = vec![0xFF, 0xFE, 0xFD];
        file.write_all(&invalid_bytes).unwrap();

        let result = read_file_with_encoding(file_path.to_str().unwrap());
        assert!(result.is_ok());
        let content = result.unwrap();

        assert!(content.contains("\u{FFFD}"));
    }

    #[test]
    fn test_empty_file() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("empty.txt");

        File::create(&file_path).unwrap();

        let result = read_file_with_encoding(file_path.to_str().unwrap());
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), "");
    }
}
