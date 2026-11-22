# 任意 B — Microsoft Foundry から Ontology を再利用する

所要時間: 30〜60 分　／　前提: [Lab 07](07-ontology.md) 完了、別途実施する Microsoft Foundry ワークショップの環境

> **この Lab で作成した Ontology は、別途実施する Microsoft Foundry ワークショップからも再利用できます。**
> 業務定義をコピーして作り直すのではなく、同じ Fabric の Ontology を Foundry の Agent の知識源として接続し、
> 同じデータに対する回答を比較する発展演習を実施できます。

このページは、本編と Foundry ワークショップをつなぐための **受け渡し情報と確認手順** をまとめたものです。
Foundry 側の詳しい操作は、Foundry ワークショップの手順書に従ってください。

## 2 つの接続方法の違い

| 方法 | 何をつなぐか | 向いている用途 |
|---|---|---|
| **Foundry IQ の知識源（推奨）** | Foundry の Agent → Fabric IQ の知識源 → `onto_taxi` | 同じ業務定義を Foundry の Agent で再利用する |
| Ontology の MCP サーバー | MCP 対応の独自 Agent → `onto_taxi` | Foundry 以外のツールや独自実装から使う |
| （参考）Data Agent の MCP | MCP 対応のクライアント → `taxi_ontology_agent` | Fabric の Data Agent ごと呼び出す（Lab 08 の方式） |

「Ontology を直接参照する」方法と「Data Agent を呼び出す」方法は別物です。Agent の指示や回答の作り方が異なるため、比較するときは区別してください。

## 必要なもの

| 必要なもの | 用意する人 | 備考 |
|---|---|---|
| Azure サブスクリプションと Foundry プロジェクト | Foundry ワークショップ | Fabric だけの受講者には不要（この演習は任意） |
| Azure AI Search と Foundry のマネージド ID への **Search Index Data Contributor** | Foundry ワークショップ | 未付与だと Foundry の Agent が 403 になる |
| 両方にアクセスできる同じアカウント | 受講者 | 別テナントの Ontology は参照できない |
| 追加の利用料金 | 講師 | Foundry のモデル・検索リソースに課金される |

## 受け渡し情報

🤖 **Copilot に入力**

```text
Foundry ワークショップで onto_taxi を知識源として使うための受け渡し情報をまとめて。
ワークスペース名と ID、Ontology の名前と ID、エンティティと関係の一覧、バインド先のテーブル、
比較用の質問と期待値を表にして、.lab/foundry-handoff.md に保存して。秘密情報は含めないで。
```

🤖 **Copilot の動き**: `lab.py check` と `lab.py ontology`（プレビューのみ）の結果、`tests/expected/agent_questions.json` から作成します。

## Foundry 側の流れ（概要）

公式手順: [Create an Ontology Agent in Foundry IQ](https://learn.microsoft.com/fabric/iq/ontology/how-to-create-agent-foundry-iq)

1. 🌐 Foundry ポータル › **Knowledge › Knowledge bases › + New knowledge base** で、種類に **Fabric IQ** を選びます。
2. OneLake カタログで自分のワークスペースの `onto_taxi` を選び、知識源を作成します。
3. 知識ベースの説明に「NYC グリーンタクシー 2026 年 4 月のトリップ・ゾーン・ベンダー」と書きます（Agent が使う場面の判断に使われます）。
4. Agent を作成し、知識ベースを追加します。
5. Lab 08 の Q1〜Q6 を同じ順に質問し、`taxi_ontology_agent` の回答（`.lab/agent-comparison.json`）と比べます。

## 確認ポイント

| 観点 | 確認すること |
|---|---|
| 同じ定義の再利用 | Foundry 側で業務定義を書き直さずに、乗車地と降車地を区別して答えたか |
| 数値 | Q1〜Q3 が期待値（37,948 件、2,340 件など）と一致したか |
| 権限 | Foundry から読めるのは、サインインしたアカウントが Fabric で読めるデータだけか |
| データの扱い | Fabric の外（Foundry）に回答が渡ることを、利用規約・社内ルールの観点で確認したか |

> [!NOTE]
> 別途作成中の Foundry ワークショップの URL と手順は、公開後にこのページへ追記してください。
