# gomc-rest (Python)

[English](README.md) / 日本語

三菱 PLC を [gomc-rest](https://github.com/Moge800/gomc-rest) 経由で操作する
Python パッケージです。**パターンB** を採用しており、`gomc-rest` サーバの
バイナリを同梱して subprocess として自動起動します。そのため利用者が exe を
自分で起動・配布する必要はありません。

HTTP 通信層は [gomc-rest-client](https://github.com/Moge800/gomc_rest_client)
が提供します。本パッケージはそこに「バイナリの同梱」と「プロセスのライフ
サイクル管理」だけを足したものです。

```text
あなたの Python プロセス
└─ gomc_rest.launch()
     ├─ 同梱 exe (gomc-rest) を空きループバックポートで起動 ── MCプロトコル ──▶ PLC
     └─ そこを指す gomc_rest_client.PLCClient を返す
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
# with を抜けると同梱サーバは自動的に停止します
```

`launch()` は `Server` を返します。context manager として使うと `PLCClient`
（read/write/remote の全 API は gomc-rest-client を参照）が得られ、終了時に
サーバを停止します。`with` を使わない場合は、インタプリタ終了時に停止します。

サーバのフラグは `extra_args` で渡せます:

```python
with gomc_rest.launch(plc_host="192.168.0.1", extra_args=["-enable-remote"]) as plc:
    plc.remote_run()
```

## アクセス制御

既定で 2 つの独立した層がサーバを保護します（両方とも有効）:

1. **起動ごとの bearer トークン。** 起動のたびにランダムなトークンを生成し、
   サーバ側で必須にします。そのため、ポートを発見した同一ホストの別プロセス
   であってもトークン無しでは API を叩けません。トークンは返却される
   クライアントへ自動設定され、`server.token` で参照できます。明示的に
   `token=` を渡せば他アプリと共有でき、`token=""` で認証を無効化できます
   （クローズドネットワーク用途）。
2. **ループバックバインド。** 既定では `127.0.0.1` にバインドするため、他の
   ホストからは到達できません。

`server_mode=True` にすると全インターフェースにバインドし、ネットワーク上の
他アプリ（gomc-rest-gui、別マシンの curl など）から呼べます。その際は
`server.token` を相手に渡してください:

```python
server = gomc_rest.launch(plc_host="192.168.0.1", server_mode=True)
print(server.base_url)   # 他アプリは http://<このホスト>:<ポート> に接続
print(server.token)      # ...このトークンを添えて
try:
    server.client.read("D100", 3)
finally:
    server.close()
```

サーバは TLS を持ちません。`server_mode` は信頼できるネットワークでのみ
有効化してください。

**脅威モデル。** トークンはコマンドライン引数ではなく `GOMCR_TOKEN` 環境変数
でサーバへ渡すため、プロセス一覧には現れません。これにより他ホスト・他 OS
ユーザからは保護されます。ただし、**同一 OS ユーザ**で動く別プロセスは
サーバの環境（例: `/proc/<pid>/environ`）を読めるため、そこに対しては保護
**できません**。ここでの信頼境界は OS ユーザです。

## バージョン

本パッケージは固定された `gomc-rest` バイナリ（現在 **v1.4.0**、`GOMC_REST_VERSION`
で指定）を同梱します。これは `gomc-rest-client` の
`MINIMUM_SUPPORTED_GOMC_REST_VERSION` を満たす必要があり、`launch()` が起動時に
検証します。依存 `gomc-rest-client` は範囲を固定（`>=0.10.0,<0.11`）しており、
将来クライアントが最低対応サーバ版を引き上げても、同梱バイナリを更新せずに
インストールが壊れることはありません。

## リリース / 同梱バイナリ

同梱サーバのバージョンは `GOMC_REST_VERSION` で固定します。バイナリは git に
コミットせず、対応する gomc-rest の GitHub リリースから取得します。

- ローカル: `python scripts/vendor_binaries.py` が 3 つのバイナリを
  `src/gomc_rest/binaries/` にダウンロードし、`checksums/<version>.sha256` に
  コミットされた信頼 SHA-256 値と照合します。
- `v*` タグの push 時: `.github/workflows/release.yml` が OS ごとに
  プラットフォーム別 wheel を 1 つずつビルド（各 wheel に対応バイナリのみ同梱）し、
  trusted publishing で PyPI に公開します。リリースジョブはタグが
  `project.version` と一致することを検証します。`workflow_dispatch` は wheel の
  検証ビルドのみで、公開は行いません。

リリース手順:

1. 同梱サーバを変更する場合は `GOMC_REST_VERSION` を編集し（固定中の
   `gomc-rest-client` が受け付ける範囲に収めること）、各アセットの信頼
   SHA-256 を記した `checksums/<version>.sha256` を追加します。新しい
   バイナリの glibc 要求が変わる場合は、`release.yml` の `plat` タグも更新します。
2. パッケージのバージョンを `pyproject.toml`（`project.version`）と
   `src/gomc_rest/__init__.py`（`__version__`）の**両方**で更新します
   （両者は一致している必要があります）。
3. そのバージョンと完全に一致するタグを切ります。例:
   `git tag v0.2.0 && git push origin v0.2.0`
   （タグが `project.version` と一致しないとリリースジョブは失敗します）。
