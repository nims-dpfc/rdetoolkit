# Using RDEToolKit with Docker

rdetoolkitを使った構造化処理をDocker上で動作させる手順をまとめます。

## ディレクトリ構造

```bash
(構造化プロジェクトディレクトリ)
├── container
│   ├── data/
│   ├── modules/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── inputdata
│   ├── input1
│   └── input2
├── README.md
└── template
    ├── batch.yaml
    ├── catalog.schema.json
    ├── invoice.schema.json
    ├── jobs.template.yaml
    ├── metadata-def.json
    └── tasksupport

```

## Dockerfile

`container/Dockerfile`を作成します。下記はDockerfileの作成例です。

使用するdockerイメージや各種実行文は、各プロジェクトで自由に変更してください。

```Dockerfile
FROM python:3.11.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py /app
COPY modules/ /app/modules/
```

!!! Reference
    docker hub

    [docker hub](https://hub.docker.com/)

## イメージの作成

`Dockerfile`が配置されているディレクトリに移動してください。docker buildコマンドを使用してビルドを実行します。コマンドの形式は次のようになります

```bash
# コマンド
$ docker build -t イメージ名:タグ パス
# 実行例
$ docker build -t sample_tif:v1 .
```

- `-t`オプションでイメージ名とタグを指定します。イメージ名は任意の名前で構いませんが、一意であることが望ましいです。
- パスには`Dockerfile`が存在するディレクトリのパスを指定します。例えば、カレントディレクトリにDockerfileがある場合は`.`を指定します。
- プロキシ環境化の場合、`--build-arg http_proxy=`, `--build-arg https_proxy=`を設定してください。

### もしpipコマンドで失敗する場合

Dockefileと同じ階層に、`pip.conf`というファイルを以下の内容で作成してください。同時に`Dockerfile`も修正してください。

```text
[install]
trusted-host =
    pypi.python.org
    files.pythonhosted.org
    pypi.org
```

修正後のDockerfile

```Dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
COPY pip.conf /etc/pip.conf

RUN pip install -r requirements.txt

COPY main.py /app
COPY modules/ /app/modules/
```

## dockerイメージを起動

ビルドしたイメージを実行するには、`docker run`コマンドを使用します。
Docker上で構造化処理をテストするため、入力ファイルのディレクトリ(dataなど)をマウントします。

```bash
$ docker run [オプション] イメージ名 [コマンド]
# 実行例
$ docker run -it -v ${HOME}/sample_tif/container/data:/app2/data --name "sample_tifv1" sample_tif:v1 "/bin/bash"
```

- `-it`: このオプションは、対話的なモードでコンテナを実行するために使用されます。コンテナとの対話が可能になり、ターミナルやコマンドラインインタフェースを利用できます。
- `-v ${HOME}/sample_tif/container/data:/app2/data`：このオプションは、ホストとコンテナ間でディレクトリをマウントするために使用されます。`${HOME}/sample_tif/container/data`はホスト側のディレクトリを指し、`/app2/data`はコンテナ内のディレクトリを指します。
- `--name "sample_tifv1"`：このオプションは、コンテナに名前を付けるために使用されます。ここでは名前をsample_tifv1として指定します。
- `sample_tif:v1`：この部分は、実行するDockerイメージの名前とバージョンを指定します。
- `"/bin/bash"`：最後の部分は、コンテナ内で実行するコマンドを指定します。ここでは、Bashシェル(/bin/bash)を使用しています。

実行すると、ターミナルがroot@(コンテナID):のように変化すると思います。

## コンテナ上でプログラムを動作させる

開発したプログラムを起動させます。

```bash
$ cd /app2
$ python3 /app/main.py
```

## コンテナを出る

以下のコマンドでコンテナを終了させます。

```bash
exit
```
