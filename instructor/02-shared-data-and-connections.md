# 講師ガイド 02 — 共有データと共有接続（Lab 03）

Lab 03 では、講師が用意した ADLS Gen2 上の CSV を、各受講者が OneLake ショートカットで参照します。
受講者は Azure の権限を持たず、**共有接続**だけを使います。

## 1. 構成

```text
ADLS Gen2（講師） ── サービスプリンシパルの資格情報 ──▶ Fabric 接続（共有、User 権限）
                                                       │
                                        各受講者の Lakehouse の Shortcut ◀─ 受講者
```

既定値は `config/workshop.json` の `sharedAdls` です。別の環境で開催する場合は
`config/workshop.local.json` に同じキーで上書きし、受講者に配布してください。

| 項目 | 既定値 |
|---|---|
| 接続名 | `adls-handson-sp-v3` |
| ADLS URL | `https://st0taxihandson0616.dfs.core.windows.net` |
| コンテナー / パス | `/taxi-data` |
| ファイル | `Taxi_zone_lookup.csv`（NYC TLC の Taxi Zone Lookup、265 行 + ヘッダー） |

## 2. 準備手順

1. ストレージアカウント（階層型名前空間を有効）を作成し、コンテナー `taxi-data` に CSV を置きます。
   CSV は [NYC TLC の Taxi Zone Lookup](https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv) を使い、
   ファイル名を `Taxi_zone_lookup.csv` にします。
2. 読み取り専用のサービスプリンシパルを作成し、ストレージに **Storage Blob Data Reader** を付与します。
   シークレットは安全な保管場所で管理し、配布物やリポジトリに記載しません。
3. Fabric の **設定 › 接続とゲートウェイの管理** で ADLS Gen2 接続を作成します（認証: サービスプリンシパル）。
4. 接続の **ユーザーの管理** で、受講者グループ（または各受講者）に **User** を付与します。
5. ネットワーク: Fabric からストレージに到達できることを確認します。公開ネットワークを全面許可する前に、
   組織のポリシー（信頼されたワークスペース アクセス、リソース インスタンス ルールなど）を確認してください。

## 3. 確認

```bash
python3 scripts/instructor/workspaces.py preflight --from 1 --to 30
```

その後、テスト受講者で Lab 03 を実行し、`nb_03_validate_dimensions` の結果が `passed: true` になることを確認します。

> [!NOTE]
> 期待値の `pickupBoroughOtherTrips: 266` は、CSV の `Unknown`（LocationID 264）と `N/A`（LocationID 265）の合計です。
> 別の版の CSV を使う場合は、`nb_03_validate_dimensions` の結果と `tests/expected/expected.json` の差を確認してください。

## 4. よくある失敗

| 症状 | 原因と対処 |
|---|---|
| ショートカット作成で接続が見つからない | 接続が受講者に共有されていない。User 権限を付与 |
| ショートカット作成で 403 / `InsufficientPrivileges` | SP にストレージの読み取り権限がない、またはネットワークで到達できない |
| CSV が読めない | `subpath` がコンテナー名から始まっていない（`/taxi-data`） |
