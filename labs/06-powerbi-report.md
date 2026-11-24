# Lab 06 — Power BI レポート

所要時間: 約 20 分　／　前提: [Lab 05](05-semantic-model.md) 完了

このラボでは、`sm_taxi` を使ったレポート `rpt_taxi_analysis` を Copilot に作成・公開してもらいます。
レポート定義（PBIR）の生成と検証は、`powerbi-authoring` プラグインの `powerbi-report-cli` スキルが担当します。

| # | ビジュアル | 使う項目 |
|---|---|---|
| 1 | KPI（総トリップ数・売上合計・平均運賃） | `Trips` / `Total Amount` / `Avg Fare` |
| 2 | 折れ線: 日別の売上合計 | `fact_trips[pickup_date]` × `Total Amount` |
| 3 | 縦棒: 時間帯別の平均運賃 | `fact_trips[pickup_hour]` × `Avg Fare` |
| 4 | 横棒: 乗車区別のトリップ数 | `dim_pickup_zone[pickup_borough]` × `Trips` |
| 5 | 表: 乗車区 × 降車区のトリップ数 | `pickup_borough` × `dropoff_borough` × `Trips` |
| 6 | スライサー: ベンダー・支払方法 | `dim_vendor[vendor_name]` / `dim_payment_type[payment_type_name]` |

---

## 6-1. レポートを作成して公開する

🤖 **Copilot に入力**

```text
sm_taxi を使って「rpt_taxi_analysis」という Power BI レポートを作って、自分のワークスペースに公開して。
タイトルは「NYC グリーンタクシー乗車分析（2026年4月）」にして、次のビジュアルを入れて:
- 上部に KPI（総トリップ数・売上合計・平均運賃）
- 日別の売上合計の折れ線
- 時間帯別の平均運賃の縦棒
- 乗車区別のトリップ数の横棒（多い順）
- 乗車区と降車区のトリップ数のマトリックス
- ベンダーと支払方法のスライサー
公開前にレポート定義を検証して、エラーが 0 件であることを確認して。
```

🤖 **Copilot の動き**

1. `sm_taxi` の表・列・メジャーを確認します。
2. `powerbi-report-author` CLI でレポート定義を生成し、検証します（エラー 0 件になるまで修正）。
3. Fabric REST API でレポートを公開し、リンクを表示します。

✅ **期待する結果**

```text
rpt_taxi_analysis: validate succeeded (errors: 0) / published
```

---

## 6-2. レポートを確認する

🌐 **ブラウザ**

1. Copilot が表示したリンクからレポートを開きます。
2. KPI が **37,948 件 / $687,602.60 / $11.92** であることを確認します。
3. マトリックスで **Manhattan → Brooklyn が 2,340 件** であることを確認します。
4. スライサーでベンダーを切り替え、各ビジュアルが連動することを確認します。

![完成イメージ（V3 のレポート例）]<img width="1163" height="650" alt="image" src="https://github.com/user-attachments/assets/636db996-2f0a-4e7b-9155-dc1bd23e2e4a" />


---

## ✅ チェックポイント

- [ ] `rpt_taxi_analysis` が公開された
- [ ] KPI・マトリックスの数値が期待値と一致した

## 🧹 トラブルシュート

| 症状 | 🤖 Copilot に入力 |
|---|---|
| カードが空白の箱になる | 「KPI をカードではなくテーブルで表示するように直して再公開して」 |
| ビジュアルにデータが出ない | 「sm_taxi の更新状態を確認して、必要なら更新して」 |
| 検証エラーが残る | 「検証エラーの内容と修正方針を説明してから直して」 |
| ライセンスエラー | Lab 05 のトラブルシュート（試用版の開始）を参照 |

デザインを磨きたい場合は [任意 A](optional-a-ux.md) へ。次は **[Lab 07 — Ontology](07-ontology.md)** です。
