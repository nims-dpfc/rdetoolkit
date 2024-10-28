use std::process::Command;

fn main() {
    // Pythonのバージョンを取得
    let python_version_output = Command::new("python3")
        .arg("-c")
        .arg("import sys; print(f'python{sys.version_info.major}.{sys.version_info.minor}')")
        .output()
        .expect("Failed to get Python version");

    let python_version = String::from_utf8(python_version_output.stdout)
        .expect("Invalid UTF-8 sequence")
        .trim()
        .to_string();

    // Pythonのライブラリをリンク
    println!("cargo:rustc-link-lib={}", python_version);

    // Pythonのインクルードディレクトリとライブラリディレクトリを設定
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
