# Lab 05 — セマンティックモデル

所要時間: 約 20 分　／　前提: [Lab 04](04-warehouse-tsql-notebook.md) 完了、Power BI Pro / PPU 相当のライセンス

このラボでは Warehouse のスター スキーマから、**Direct Lake** のセマンティックモデル `sm_taxi` を作成します。

## セマンティックモデルとは

レポートや AI が「どの表をどうつなぎ、何をどう計算するか」を共有するための分析用モデルです。

| 要素 | `sm_taxi` での例 |
|---|---|
| 表と関係 | `fact_trips` と 6 つのディメンションを多対一で関連付け |
| メジャー（計算の定義） | `Trips`、`Total Amount`、`Avg Fare`、`Max Fare`、`Avg Trip Distance` |
| 接続モード | Direct Lake（OneLake の Delta を直接読む。データのコピーや資格情報の設定が不要） |

```text
dim_vendor ─┐   dim_ratecode ─┐   dim_payment_type ─┐   dim_trip_type ─┐
            └──────────────── fact_trips ───────────┴────────────────┘
               PULocationID ─▶ dim_pickup_zone    DOLocationID ─▶ dim_dropoff_zone
```

乗車地と降車地は、**別々のディメンション**にしています。1 つのゾーン表に 2 本の関係を張ると片方が非アクティブになり、
「Manhattan で乗って Brooklyn で降りた」のような質問を AI が正しく解釈しにくくなるためです。

> V3 では Import と DirectQuery が章ごとに混在し、支払方法がファクトと未結合でした。V4 は Direct Lake に統一し、6 本すべての関係を張っています。

---

## 5-1. モデル定義を確認してから作成する

🤖 **Copilot に入力**

```text
Lab 05 のセマンティックモデル sm_taxi の定義を生成して、表・関係・メジャーの内容を要約して見せて。
問題がなければ、そのまま自分のワークスペースに作成して、最新のデータを読み込ませて。
```

🤖 **Copilot の動き**

1. `python3 scripts/lab.py semantic-model` で TMDL を生成し、`.lab/semantic-model/` に保存して内容を要約します。
2. `python3 scripts/lab.py semantic-model --apply` で作成（既にあれば更新）し、Direct Lake の更新（フレーミング）を実行します。

✅ **期待する結果**: `sm_taxi` が作成され、更新が `Completed`。

---

## 5-2. モデルの数値を期待値と照合する

🤖 **Copilot に入力**

```text
sm_taxi に DAX で問い合わせて、主要な数値が教材の期待値と一致するか確認して。
総トリップ数、売上合計、平均運賃、最大運賃、平均距離、Manhattan から Brooklyn、ベンダー別、支払方法別を比べて。
```

🤖 **Copilot の動き**: `python3 scripts/lab.py model-check`（Power BI の Execute Queries API で DAX を実行）

✅ **期待する結果**: `passed: true`

| メジャー | 期待値 |
|---|---|
| Trips | 37,948 |
| Total Amount | $687,602.60 |
| Avg Fare | $11.92 |
| Max Fare | $67.68 |
| Avg Trip Distance | 3.49 |
| Manhattan → Brooklyn | 2,340 件 / $42,944.85 |
| ベンダー別 | 1（Creative Mobile）18,905 / 2（VeriFone）19,043 |
| 支払方法別 | 1（Credit card）24,637 / 2（Cash）13,311 |

🌐 **ブラウザ**（任意）: ポータルで `sm_taxi` を開き、**データ モデルを開く** で関係図を確認します。

---

## ✅ チェックポイント

- [ ] `sm_taxi` が Direct Lake で作成され、更新が完了した
- [ ] `model-check` が `passed: true`

## 🧹 トラブルシュート

| 症状 | 対処 |
|---|---|
| 作成時にライセンスエラー | 🌐 Power BI の試用版を開始（[サインイン手順](fabric-portal-login.md)）してから 🤖「sm_taxi をもう一度作成して」 |
| 更新が Failed | 🤖「sm_taxi の更新エラーの内容を表示して」。Warehouse のテーブル名・列名の不一致が多い |
| 数値が一致しない | 🤖「model-check の不一致項目と Lab 04 の検証結果を比べて原因を教えて。データは変更しないで」 |
| Execute Queries が 401/403 | テナント設定（Dataset Execute Queries REST API）を講師に確認 |

次は **[Lab 06 — Power BI レポート](06-powerbi-report.md)** です。
