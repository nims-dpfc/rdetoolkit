use pyo3::prelude::*;
mod imageutil;

#[pymodule]
pub fn rdetoolkit_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(
        imageutil::processing::resize_image_aspect_ratio,
        module
    )?)?;
    Ok(())
}
