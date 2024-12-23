use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
mod charset_detector;
mod imageutil;

#[pymodule]
pub fn core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(
        imageutil::processing::resize_image_aspect_ratio,
        module
    )?)?;

    module.add_function(wrap_pyfunction!(charset_detector::detect_encoding, module)?)?;

    module.add_function(wrap_pyfunction!(
        charset_detector::read_file_with_encoding,
        module
    )?)?;

    Ok(())
}
