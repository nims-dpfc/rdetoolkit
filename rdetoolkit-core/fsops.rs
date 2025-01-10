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
    use tempfile::tempdir;

    #[test]
    fn test_managed_directory_new() -> PyResult<()> {
        Python::with_gil(|_py| {
            let temp = tempdir().unwrap();
            let base_dir = temp.path().to_str().unwrap();
            let dir = ManagedDirectory::new(base_dir, "test_dir", None, None)?;

            assert_eq!(dir.n_digit, 4);
            assert_eq!(dir.idx, 0);
            assert!(dir.path.ends_with("test_dir"));
            assert!(dir.path.exists());

            Ok(())
        })
    }

    #[test]
    fn test_managed_directory_with_index() -> PyResult<()> {
        Python::with_gil(|_py| {
            let temp = tempdir().unwrap();
            let base_dir = temp.path().to_str().unwrap();
            let dir = ManagedDirectory::new(base_dir, "test_dir", Some(3), Some(1))?;

            let expected_path = Path::new("divided").join("001").join("test_dir");

            assert!(dir.path.ends_with(&expected_path));
            assert!(dir.path.exists());

            Ok(())
        })
    }

    #[test]
    fn test_managed_directory_call() -> PyResult<()> {
        Python::with_gil(|_py| {
            let temp = tempdir().unwrap();
            let base_dir = temp.path().to_str().unwrap();
            let dir = ManagedDirectory::new(base_dir, "test_dir", None, None)?;

            let new_dir = dir.__call__(1)?;
            let expected_path = Path::new("divided").join("0001").join("test_dir");

            assert!(new_dir.path.ends_with(&expected_path));
            assert!(new_dir.path.exists());

            let err = dir.__call__(-1);
            assert!(err.is_err());

            Ok(())
        })
    }

    #[test]
    fn test_managed_directory_list() -> PyResult<()> {
        Python::with_gil(|_py| {
            let temp = tempdir().unwrap();
            let base_dir = temp.path().to_str().unwrap();
            let dir = ManagedDirectory::new(base_dir, "test_dir", None, None)?;

            let test_file = dir.path.join("test.txt");
            fs::write(&test_file, "test").unwrap();

            let files = dir.list()?;
            assert_eq!(files.len(), 1);
            assert!(files[0].contains("test.txt"));

            Ok(())
        })
    }

    #[test]
    fn test_managed_directory_string_representation() -> PyResult<()> {
        Python::with_gil(|_py| {
            let temp = tempdir().unwrap();
            let base_dir = temp.path().to_str().unwrap();
            let dir = ManagedDirectory::new(base_dir, "test_dir", None, None)?;

            assert!(dir.__str__().contains("test_dir"));
            assert!(dir.__repr__().starts_with("ManagedDirectory"));
            Ok(())
        })
    }

    #[test]
    fn test_directory_ops_new() -> PyResult<()> {
        Python::with_gil(|_py| {
            let temp = tempdir().unwrap();
            let base_dir = temp.path().to_str().unwrap();

            let ops = DirectoryOps::new(base_dir, None)?;
            assert_eq!(ops.n_digit, 4);
            assert!(ops.base_dir.exists());

            // カスタム桁数でインスタンス生成
            let ops_custom = DirectoryOps::new(base_dir, Some(6))?;
            assert_eq!(ops_custom.n_digit, 6);

            Ok(())
        })
    }

    #[test]
    fn test_directory_ops_gettattr() -> PyResult<()> {
        Python::with_gil(|_py| {
            let temp = tempdir().unwrap();
            let base_dir = temp.path().to_str().unwrap();
            let ops = DirectoryOps::new(base_dir, None)?;

            let test_dir = ops.__getattr__("test_directory")?;
            assert!(test_dir.path.exists());
            assert_eq!(test_dir.n_digit, 4);
            assert_eq!(test_dir.idx, 0);

            Ok(())
        })
    }

    #[test]
    fn test_directory_ops_repr() -> PyResult<()> {
        Python::with_gil(|_py| {
            let temp = tempdir().unwrap();
            let base_dir = temp.path().to_str().unwrap();
            let ops = DirectoryOps::new(base_dir, None)?;

            let repr = ops.__repr__();
            assert!(repr.contains("DirectoryOps"));
            assert!(repr.contains("n_digit=4"));
            assert!(repr.contains(base_dir));

            Ok(())
        })
    }

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
