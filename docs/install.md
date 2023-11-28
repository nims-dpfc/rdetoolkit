# インストール方法

rdetoolkitは、現在、NIMS所内GitLab Package Regisotryに配置されています。そのため、以下のコマンドを実行しライブラリのインストールを行なってください。

!!! Warning
    NIMS所外からのインストールを実行する場合、RDEへご連絡ください。

## install

```shell
pip install rdetoolkit --index-url https://<access_token_name>:<access_token>@gitlab.nims.go.jp/api/v4/projects/648/packages/pypi/simple
```

## requirements.txt

`requirements.txt`に記載する場合、以下のように記載してください。

```text
#requirements.txt

-i https://<access_token_name>:<access_token>@gitlab.nims.go.jp/api/v4/projects/648/packages/pypi/simple
rdetoolkit>=0.1.1

```

!!! Tip
    <access_token_name>と<access_token>は、個人のアクセストークンもしくは、WikiのRDE開発者ドキュメントにインストール用のトークンを掲載しています。そちらのドキュメントを参照してインストールしてください。
