# 講師ガイド 01 — テナント・容量・ユーザー

## 1. 容量

| 項目 | 推奨 | 理由 |
|---|---|---|
| 種類 | **有料 F 容量**（F32 以上を推奨。人数で調整） | Data Agent・Copilot は Fabric Trial 容量では使えません |
| リージョン | Fabric Apps・Ontology・Data Agent が使えるリージョン | 機能ごとに提供リージョンが異なります |
| 稼働 | 開催前日に Active を確認、終了後に一時停止 | 停止中はすべての Lab が失敗します |

> [!WARNING]
> Spark は同時実行数の上限があります。受講者全員が同時に Notebook を実行すると、ジョブが待機（キュー）状態になります。
> リハーサルで「受講者数 × Lab 02 の Notebook 2 本」を同時に流し、待ち時間を確認してください。
> 待ちが長い場合は、グループごとに開始時刻をずらすか、容量を一時的にスケールアップします。

## 2. テナント設定（Fabric 管理ポータル）

**OneLake カタログ › 管理 › 構成 › テナント設定** で、受講者を含むセキュリティグループに対して有効化します。
設定の反映には最大 1 時間かかるため、**開催の 1 時間以上前**に完了してください。

| 設定 | 使う Lab |
|---|---|
| Users can create Fabric items | 全 Lab |
| Users can create ontology (preview) items | Lab 07 |
| Users can use Copilot and other features powered by Azure OpenAI | Lab 08 |
| Capacities can be designated as Fabric Copilot capacities | Lab 08 |
| Data sent to Azure OpenAI can be processed outside your capacity's geographic region...（容量が米国・EU 以外の場合） | Lab 08 |
| Data sent to Azure OpenAI can be stored outside your capacity's geographic region...（同上） | Lab 08 |
| Fabric data agent の作成・共有に関する設定 | Lab 08 |
| Fabric Apps（preview）ワークロード | Lab 09 |
| Dataset Execute Queries REST API | Lab 09（セマンティックモデル connector） |

参照: [Data Agent のテナント設定](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings)、
[Ontology チュートリアルの前提条件](https://learn.microsoft.com/fabric/iq/ontology/tutorial-0-introduction#prerequisites)、
[Fabric Apps の前提条件](https://learn.microsoft.com/fabric/apps/create-app-with-cli#prerequisites)

## 3. ユーザーとライセンス

1. `config/workshop.json` の `accountPrefix`・`accountDomain` に合わせて `student<番号>@<ドメイン>` を作成します。
2. 受講者をまとめるセキュリティグループ（例: `fabric-handson-students`）に追加し、上記テナント設定の対象にします。
3. Lab 05・06 のため、Power BI Pro / PPU 相当を割り当てるか、受講者が個人トライアルを開始できるようにします。
4. 条件付きアクセスで、Codespaces（デバイスコード）からのサインインがブロックされないことを確認します。
   **デバイスコードフローをブロックするポリシーがある場合は、Lab 01 の主経路が使えません。** 例外の要否を管理者と事前に決めてください。
5. 配布アカウントで MFA を要求する場合は、受講者に Microsoft Authenticator の準備を事前案内します。

## 4. 受講者ワークスペース

補助スクリプトで作成と確認ができます（講師アカウントで Azure CLI にサインインして実行。既定は計画表示のみ）。

```bash
az login --tenant <tenantId> --allow-no-subscriptions
python3 scripts/instructor/workspaces.py provision --from 1 --to 30 --capacity "<容量の表示名>"           # 計画を確認
python3 scripts/instructor/workspaces.py provision --from 1 --to 30 --capacity "<容量の表示名>" --apply   # 実行
python3 scripts/instructor/workspaces.py preflight --from 1 --to 30
```

- ワークスペース名は `student<番号>`、受講者には **Member** を付与します（Fabric Apps の作成に Contributor 以上が必要）。
- 番号を 0 埋めする場合（`student01`）は `--pad` を付け、受講者にも 0 埋めの番号を配布します。
- ユーザーの検索に `az ad user show` を使うため、Entra のユーザー読み取り権限が必要です。

## 5. 確認

`preflight` がすべて `OK` になり、テスト受講者 2 名で [04 リハーサル](04-rehearsal-and-runbook.md) の Gate を通過したら完了です。
