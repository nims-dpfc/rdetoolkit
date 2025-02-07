# API Documentation

## modules

- [workflows](workflows): ワークフローの定義と管理を行うモジュール。
- [config](config): 設定ファイルの読み込みと管理を行うモジュール。
- [fileops](fileops): RDE関連のファイル操作を提供するモジュール。
- [rde2util](rde2util): RDE関連のユーティリティ関数を提供するモジュール。
- [invoicefile](invoicefile): 送り状ファイルの処理を行うモジュール。
- [validation](validation): データの検証を行うモジュール。
- [modeproc](modeproc): モード処理を行うモジュール。
- [img2thumb](img2thumb): 画像をサムネイルに変換するモジュール。
- [rdelogger](rdelogger): ロギング機能を提供するモジュール。
- [errors](errors): エラーハンドリングを行うモジュール。
- [exceptions](exceptions): 例外処理を行うモジュール。

## models

- [config](models/config): 設定ファイルの読み込みと管理を行うモジュール。
- [invoice_schema](models/invoice_schema): 送り状のスキーマを定義するモジュール。
- [invoice](models/invoice): 送り状やExcelinvoiceの情報を定義するモジュール。
- [metadata](models/metadata): メタデータの管理を行うモジュール。
- [rde2types](models/rde2types): RDE関連の型定義を提供するモジュール。
- [result](models/result): 処理結果を管理するモジュール。

## impl

- [compressed_controller](impl/compressed_controller): 圧縮ファイルの管理を行うモジュール。
- [input_controller](impl/input_controller): 入力モードの管理を行うモジュール。

## interface

- [filechecker](interface/filechecker)

## cmd

- [command](cmd/command)
