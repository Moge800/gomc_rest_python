# gomc-rest (Python)

[English](README.md) / 日本語

**三菱PLCと通信するためのPythonライブラリです。** MCプロトコル（SLMP）で
PLCのデバイスを読み書きできます。プロトコルの面倒は同梱した
[gomc-rest](https://github.com/Moge800/gomc-rest) サーバーが見てくれるので、
利用者がサーバーの実行ファイルを別途用意したり、手動で起動したりする
必要はありません。

**おまけ — REST公開機能。** 同梱サーバーは、ネットワーク上の他アプリ
（GUI、別のコンピューター、別の言語など）へ公開することもできます。また
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
ない環境（macOS、Windows arm64、glibc 2.34未満など）でも利用できます。
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
（現在は **v1.4.0**）。`launch()` は起動時に、サーバーが
`gomc-rest-client` の `MINIMUM_SUPPORTED_GOMC_REST_VERSION` を満たしているか
確認します。

`gomc-rest-client` の依存バージョンも `>=0.10.0,<0.11` に制限しています。
これにより、より新しいサーバーを必要とするクライアントが意図せず
インストールされることを防ぎます。

## リリースと同梱バイナリ

バイナリはGitリポジトリへコミットせず、対応するgomc-restのGitHub Releaseから
取得します。

- ローカルでは `python scripts/vendor_binaries.py` を実行すると、3種類の
  バイナリが `src/gomc_rest/binaries/` にダウンロードされます。各ファイルは
  `checksums/<version>.sha256` に記録されたSHA-256ハッシュと照合されます。
- `v*` タグをpushすると、`.github/workflows/release.yml` がOS別の `wheel` と
  クライアント専用の `sdist` をビルドし、PyPIのTrusted Publishingを使用して
  公開します。`workflow_dispatch` では検証用のビルドのみを行い、公開しません。

### リリース手順

1. 同梱サーバーを変更する場合は `GOMC_REST_VERSION` を更新し、各バイナリの
   SHA-256ハッシュを記載した `checksums/<version>.sha256` を追加します。
   必要なglibcバージョンが変わる場合は、`release.yml` の `plat` タグも更新します。
2. `pyproject.toml` の `project.version` と
   `src/gomc_rest/__init__.py` の `__version__` を同じバージョンへ更新します。
3. パッケージバージョンと同じタグを作成してpushします。

```bash
git tag v0.2.0
git push origin v0.2.0
```
