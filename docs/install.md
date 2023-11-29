# インストール方法

rdetoolkitは、現在、NIMS所内GitLab Package Regisotryに配置されています。そのため、以下のコマンドを実行しライブラリのインストールを行なってください。

インストールは、下記コマンドを実行してください。

```shell
pip install --index-url https://<access_token_name>:<access_token>@gitlab.nims.go.jp/api/v4/projects/648/packages/pypi/simple --no-deps rdetoolkit
```

`requirements.txt`に記載する場合、以下のように記載してください。

```text
#requirements.txt

-i https://get_rdetoolkit_package_group:muZ5VDUyzi4sxYckNjxY@gitlab.nims.go.jp/api/v4/projects/648/packages/pypi/simple
rdetoolkit==0.1.1

```

> <access_token_name>と<access_token>は、個人のアクセストークンもしくは、WikiのRDE開発者ドキュメントにインストール用のトークンを掲載しています。そちらのドキュメントを参照してインストールしてください。
