# gomc-rest (Python)

[English](README.md) / 日本語

**三菱PLCと通信するためのPythonライブラリです。** MCプロトコル（3E/4Eフレーム）で
PLCのデバイスを読み書きできます。MCプロトコル通信は同梱の
[gomc-rest](https://github.com/Moge800/gomc-rest) サーバーが処理するため、
利用者がサーバーの実行ファイルを別途用意したり、手動で起動したりする
必要はありません。

**追加機能 — REST APIのネットワーク公開。** `server_mode` を有効にすると、
同梱サーバーのREST APIをネットワークから利用可能にし、他のアプリケーション
（GUI、別のコンピューター、別の言語のクライアントなど）から呼び出せます。また
`connect()` を使えば、すでに別の場所で稼働している gomc-rest へ
クライアントとして接続できます（「アクセス制御」を参照）。

内部のHTTPクライアント機能には
[gomc-rest-client](https://github.com/Moge800/gomc_rest_client) を使用しています。
このパッケージが追加するのは、サーバーバイナリの同梱とプロセスの
ライフサイクル管理です。

```text
Pythonプロセス
└─ gomc_rest.launch()
     ├─ 同梱されたgomc-restをループバックアドレス上の空きポートで起動
     │    └─ MCプロトコルでPLCと通信
     └─ 起動したサーバーに接続するgomc_rest_client.PLCClientを提供
```

## インストール

```bash
pip install gomc-rest
```

## 使い方

```python
import gomc_rest

with gomc_rest.launch(plc_host="192.168.0.1") as plc:
    values = plc.read("D100", 3)
    plc.write("D100", [10, 20, 30])
# withブロックを抜けると、同梱サーバーは自動的に停止します
```

`launch()` は、サーバープロセスを管理する `Server` オブジェクトを返します。
コンテキストマネージャーとして使用すると、`with` ブロック内では
`PLCClient` を利用でき、終了時にサーバーが停止します。`with` を使わない場合も、
Pythonインタープリターの終了時にサーバーは停止します。

サーバーの追加オプションは `extra_args` で指定できます。

```python
with gomc_rest.launch(plc_host="192.168.0.1", extra_args=["-enable-remote"]) as plc:
    plc.remote_run()
```

### クライアントモード（既存のサーバーに接続する）

共有サーバーや別のコンピューターなど、すでに稼働しているgomc-restへ
接続する場合は `connect()` を使用します。同梱バイナリは起動されません。

```python
with gomc_rest.connect("http://192.168.0.1:8080", token="...") as plc:
    plc.read("D100", 3)
```

`connect()` は `PLCClient` を直接返します。`launch()` もコンテキスト
マネージャー内では同じ `PLCClient` を提供するため、どちらの起動方式でも
同じ読み書きAPIを利用できます。

`connect()` は同梱バイナリを必要としないため、対応するビルド済み `wheel` が
ない環境（Windows arm64、glibc 2.34未満、macOS 12未満など）でも利用できます。
その場合、`pip install gomc-rest` は `sdist` からパッケージをインストールします。
`connect()` は利用できますが、`launch()` を実行すると、対応するバイナリが
ないことを示すエラーが発生します。

## アクセス制御

`launch()` で起動するサーバーは、デフォルトで次の二重の保護を使用します。

1. **起動ごとのBearerトークン**

   起動時にランダムなトークンを生成し、サーバーとクライアントの両方へ
   自動設定します。明示的な `token=` を指定すれば、別のアプリケーションと
   トークンを共有できます。`token=""` を指定すると認証を無効化できます。
2. **ループバックアドレスへのバインド**

   デフォルトでは `127.0.0.1` で待ち受けるため、別のコンピューターからは
   接続できません。

`server_mode=True` を指定すると、すべてのネットワークインターフェースで
待ち受けます。gomc-rest-guiや別のコンピューター上のcurlなどから接続する場合は、
`server.token` の値を接続元へ渡してください。

```python
server = gomc_rest.launch(plc_host="192.168.0.1", server_mode=True)
print(server.base_url)  # ローカル接続用URL。外部からは127.0.0.1をホストのIPへ置換
print(server.token)     # 接続元で使用するBearerトークン
try:
    server.client.read("D100", 3)
finally:
    server.close()
```

サーバーはTLSに対応していません。`server_mode=True` は、信頼できる
ネットワーク内でのみ使用してください。

**脅威モデル:** トークンはコマンドライン引数ではなく、`GOMCR_TOKEN`
環境変数を通じてサーバーへ渡されるため、通常のプロセス一覧には表示されません。
これにより、別のホストや別のOSユーザーからのアクセスを防ぎます。一方、
同じOSユーザーで動作するプロセスは、サーバーの環境変数
（例: `/proc/<pid>/environ`）を読み取れる可能性があります。同一OSユーザーの
プロセスは信頼されているものとして扱います。

## バージョン

同梱するgomc-restのバージョンは `GOMC_REST_VERSION` で固定しています
（現在は **v1.5.0**）。`launch()` は起動時に、サーバーが
`gomc-rest-client` の `MINIMUM_SUPPORTED_GOMC_REST_VERSION` を満たしているか
確認します。

`gomc-rest-client` の依存バージョンも `>=0.10.0,<0.11` に制限しています。
これにより、より新しいサーバーを必要とするクライアントが意図せず
インストールされることを防ぎます。

## 開発者向け

リリース手順と同梱バイナリの管理方法は
[RELEASING.md](https://github.com/Moge800/gomc_rest_python/blob/main/RELEASING.md)
を参照してください。
