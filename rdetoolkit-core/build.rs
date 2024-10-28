use std::env;
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
}
