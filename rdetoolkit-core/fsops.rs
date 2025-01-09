use pyo3::exceptions::{PyFileNotFoundError, PyIOError, PyPermissionError, PyValueError};
use pyo3::prelude::*;
use pyo3::PyErr;
use std::fs;
use std::io::{Error as IoError, ErrorKind};
use std::path::{Path, PathBuf};

fn map_io_err(e: &IoError, context: &str, path: &Path) -> PyErr {
    #[cfg(debug_assertions)]
    eprintln!(
        "[DEBUG] I/O error: {}: path={}. error={}",
        context,
        path.display(),
        e,
    );

    match e.kind() {
        ErrorKind::NotFound => PyFileNotFoundError::new_err(format!(
            "{} failed: File or directory not found: {}",
            context,
            path.display(),
        )),
        ErrorKind::PermissionDenied => {
            PyPermissionError::new_err(format!("{} failed: Permission denied.", context))
        }
        _ => PyIOError::new_err(format!("{} failed: An I/O error occurred.", context,)),
    }
}

#[pyclass]
#[derive(Clone)]
pub struct ManagedDirectory {
    base_dir: PathBuf,
    dirname: String,
    n_digit: usize,
    #[pyo3(get, set)]
    idx: i32,
    path: PathBuf,
}

#[pymethods]
impl ManagedDirectory {
    #[new]
    #[pyo3(signature = (base_dir, dirname, n_digit=None, idx=None))]
    fn new(
        base_dir: &str,
        dirname: &str,
        n_digit: Option<usize>,
        idx: Option<i32>,
    ) -> PyResult<Self> {
        let n_digit = n_digit.unwrap_or(4);
        let idx = idx.unwrap_or(0);
        let base_dir = PathBuf::from(base_dir);

        let path = if idx == 0 {
            base_dir.join(dirname)
        } else {
            let divided_dir =
                base_dir
                    .join("divided")
                    .join(format!("{:0width$}", idx, width = n_digit));
            divided_dir.join(dirname)
        };

        fs::create_dir_all(&path).map_err(|e| map_io_err(&e, "create_dir_all", &path))?;

        Ok(ManagedDirectory {
            base_dir,
            dirname: dirname.to_string(),
            n_digit,
            idx,
            path,
        })
    }

    #[getter]
    fn get_path(&self) -> PyResult<String> {
        Ok(self.path.to_string_lossy().to_string())
    }

    fn create(&self) -> PyResult<()> {
        fs::create_dir_all(&self.path).map_err(|e| map_io_err(&e, "create_dir_all", &self.path))?;
        Ok(())
    }

    fn list(&self) -> PyResult<Vec<String>> {
        let entries =
            fs::read_dir(&self.path).map_err(|e| map_io_err(&e, "read_dir", &self.path))?;

        let mut result = Vec::new();
        for entry in entries {
            let entry = entry.map_err(|e2| map_io_err(&e2, "read_dir -> entry", &self.path))?;
            result.push(entry.path().to_string_lossy().to_string());
        }
        Ok(result)
    }

    #[pyo3(signature = (idx))]
    fn __call__(&self, idx: i32) -> PyResult<Self> {
        if idx < 0 {
            return Err(PyValueError::new_err("Index must be non-negative"));
        }

        let path = if idx == 0 {
            self.base_dir.join(&self.dirname)
        } else {
            let divided_dir = self.base_dir.join("divided").join(format!(
                "{:0width$}",
                idx,
                width = self.n_digit
            ));
            divided_dir.join(&self.dirname)
        };

        fs::create_dir_all(&path).map_err(|e| map_io_err(&e, "cerate_dir_all (call)", &path))?;

        Ok(Self {
            base_dir: self.base_dir.clone(),
            dirname: self.dirname.clone(),
            n_digit: self.n_digit,
            idx,
            path,
        })
    }

    fn __str__(&self) -> String {
        self.path.to_string_lossy().to_string()
    }

    fn __repr__(&self) -> String {
        format!("ManagedDirectory(path={})", self.path.display())
    }
}

#[pyclass]
#[derive(Clone)]
pub struct DirectoryOps {
    base_dir: PathBuf,
    n_digit: usize,
}

#[pymethods]
impl DirectoryOps {
    #[new]
    #[pyo3(signature = (base_dir, n_digit=None))]
    fn new(base_dir: &str, n_digit: Option<usize>) -> PyResult<Self> {
        let n_digit = n_digit.unwrap_or(4);
        let base_dir = PathBuf::from(base_dir);

        fs::create_dir_all(&base_dir)
            .map_err(|e| map_io_err(&e, "create_dir_all (base_dir)", &base_dir))?;

        Ok(DirectoryOps { base_dir, n_digit })
    }

    fn __getattr__(&self, name: &str) -> PyResult<ManagedDirectory> {
        let path = self.base_dir.join(name);

        fs::create_dir_all(&path).map_err(|e| map_io_err(&e, "create_dir_all(subdir)", &path))?;

        Ok(ManagedDirectory {
            base_dir: self.base_dir.clone(),
            dirname: name.to_string(),
            n_digit: self.n_digit,
            idx: 0,
            path,
        })
    }

    fn all(&self) -> PyResult<Vec<String>> {
        let supported_dirs = vec![
            "invoice",
            "invoice_patch",
            "inputdata",
            "structured",
            "temp",
            "logs",
            "meta",
            "thumbnail",
            "main_image",
            "other_image",
            "attachment",
            "nonshared_raw",
            "raw",
            "tasksupport",
        ];

        let mut result = Vec::new();
        for dirname in supported_dirs {
            let path = self.base_dir.join(dirname);
            fs::create_dir_all(&path)
                .map_err(|e| map_io_err(&e, "create_dir_all (supported_dirs)", &path))?;
            result.push(path.to_string_lossy().into_owned());
        }
        Ok(result)
    }

    fn __repr__(&self) -> String {
        format!(
            "DirectoryOps(base_dir={}, n_digit={})",
            self.base_dir.display(),
            self.n_digit
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    // use pyo3::types::PyType;
    use pyo3::Python;
    use std::io::{Error as IoError, ErrorKind};
    use std::path::PathBuf;

    #[test]
    fn test_map_io_err_not_found() {
        Python::with_gil(|py| {
            let e = IoError::new(ErrorKind::NotFound, "some error message");
            let path = PathBuf::from("/not/found/path");
            let err = map_io_err(&e, "test_context", &path);

            assert!(err.is_instance_of::<PyFileNotFoundError>(py));

            let err_msg = err.to_string();
            assert!(err_msg.contains("File or directory not found"));
            assert!(err_msg.contains("/not/found/path"));
        });
    }

    #[test]
    fn test_map_io_err_permission_denied() {
        Python::with_gil(|py| {
            let e = IoError::new(ErrorKind::PermissionDenied, "some error message");
            let path = PathBuf::from("/some/protected/path");
            let err = map_io_err(&e, "perm context", &path);

            assert!(err.is_instance_of::<PyPermissionError>(py));

            let err_msg = err.to_string();
            assert!(err_msg.contains("Permission denied"));
            assert!(!err_msg.contains("/some/protected/path"));
        });
    }

    #[test]
    fn test_map_io_err_other() {
        Python::with_gil(|py| {
            let e = IoError::new(ErrorKind::Other, "some io error");
            let path = PathBuf::from("/path/to/other/error");
            let err = map_io_err(&e, "other context", &path);

            assert!(err.is_instance_of::<PyIOError>(py));

            let err_msg = err.to_string();
            assert!(err_msg.contains("An I/O error occurred."))
        })
    }
}
