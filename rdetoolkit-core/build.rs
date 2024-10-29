use std::process::Command;

fn main() {
    if cfg!(target_os = "windows") {
        let python_include = Command::new("python")
            .arg("-c")
            .arg("import sysconfig;print(sysconfig.get_path('include'))")
            .output()
            .expect("Failed to get Python include directory");

        let python_include = String::from_utf8(python_include.stdout)
            .expect("Invalid UTF-8")
            .trim()
            .to_string();

        let python_libs = Command::new("python")
            .arg("-c")
            .arg("import sysconfig; print(sysconfig.get_config_var('LIBDIR'))")
            .output()
            .expect("Failed to get Python lib path");

        let python_libs = String::from_utf8(python_libs.stdout)
            .expect("Invalid UTF-8")
            .trim()
            .to_string();

        let version = Command::new("python")
            .arg("-c")
            .arg("import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
            .output()
            .expect("Failed to get Python version");

        let version = String::from_utf8(version.stdout)
            .expect("Invalid UTF-8")
            .trim()
            .to_string();

        println!("cargo:rustc-link-search=native={}", python_libs);
        println!("cargo:rustc-link-lib=python{}", version);
        println!("cargo:include={}", python_include);
    } else {
        // Unix系OSの場合
        let python_version_output = Command::new("python3")
            .arg("-c")
            .arg("import sys; print(f'python{sys.version_info.major}.{sys.version_info.minor}')")
            .output()
            .expect("Faild to get Python version");

        let python_version = String::from_utf8(python_version_output.stdout)
            .expect("Invalid UTF-8 sequence")
            .trim()
            .to_string();

        println!("cargo:rustc-link-lib={}", python_version);

        let python_include_dir = Command::new("python3")
            .arg("-c")
            .arg("from distutils.sysconfig import get_python_inc; print(get_python_inc())")
            .output()
            .expect("Failed to get Python include directory");

        let python_lib_dir = Command::new("python3")
            .arg("-c")
            .arg("import sysconfig; print(sysconfig.get_config_var('LIBDIR'))")
            .output()
            .expect("Failed to get Python library directory");

        let python_include_dir = String::from_utf8(python_include_dir.stdout)
            .expect("Invalid UTF-8 sequence")
            .trim()
            .to_string();

        let python_lib_dir = String::from_utf8(python_lib_dir.stdout)
            .expect("Invalid UTF-8 sequence")
            .trim()
            .to_string();

        println!("cargo:include={}", python_include_dir);
        println!("cargo:rustc-link-search=native={}", python_lib_dir);
    }
}
