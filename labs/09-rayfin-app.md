# Lab 09 — Fabric App（Rayfin）でダッシュボード・入力・チャット

所要時間: 約 35 分　／　前提: [Lab 05](05-semantic-model.md) と [Lab 08](08-data-agents.md) 完了

このラボでは、Rayfin CLI で Fabric App `taxi-insights` を作り、自分のワークスペースに公開します。

| 機能 | データの流れ | 誰の権限で動くか |
|---|---|---|
| ダッシュボード | アプリ → セマンティックモデル connector → `sm_taxi` | アプリを開いたユーザー |
| 入力フォーム | アプリ → アプリ専用 DB（Fabric SQL Database。OneLake にミラー） | アプリを開いたユーザー |
| チャット | アプリ → Rayfin Function → `taxi_metrics_agent` の MCP | アプリの所有者（あなた） |

## V3 からの改善点

V3 では、Codespaces で Rayfin のログインが進まずトークンを手で渡す必要があり、チャットは未同梱の中継プロキシに依存していました。

| 課題 | V4 の対処 |
|---|---|
| Codespaces で `rayfin login` が止まる（ブラウザの戻り先がコンテナー内の localhost） | `scripts/rayfin_az.py` が Azure CLI のサインインを照合し、Fabric トークンを **1 回の Rayfin 実行にだけ** 渡す |
| トークンをシェルや `.env` に置いていた | 表示・保存・export をしない。期限切れなら同じコマンドを再実行するだけ |
| チャットに外部プロキシが必要だった | Rayfin Functions から Data Agent の MCP を呼ぶ（トークンはサーバー側だけで使用） |

> 📖 認証の詳細は [講師ガイド 03](../instructor/03-app-and-agent-auth.md) を参照してください。

---

## 9-1. Rayfin プロジェクトを作成する

🤖 **Copilot に入力**

```text
教材フォルダーの apps 配下に、Rayfin の blankapp テンプレートで taxi-insights プロジェクトを作って。
バージョンは教材で検証済みのものを使って。作成後、プロジェクト内の AGENTS.md と Rayfin のスキルを読んで、
このあと使う機能（セマンティックモデル、アプリのデータ、Functions、Fabric Data Agent）の手順を確認して。
```

🤖 **Copilot の動き**

```bash
mkdir -p apps && cd apps
npx -y @microsoft/create-rayfin@2.0.1 --project-name taxi-insights --template blankapp
```

- 作成されたプロジェクトの `AGENTS.md`（機能の選び方）と `.agents/skills/` を読み、以降はその手順に従います。

✅ **期待する結果**: `apps/taxi-insights/` が作成され、`npm run typecheck` が成功する。

---

## 9-2. Rayfin の認証を確認する（環境で方法が異なります）

### Codespaces・リモート環境の場合（推奨）

🤖 **Copilot に入力**

```text
Codespaces なので rayfin login は使わずに、教材の Rayfin 認証ラッパーで、
登録済みのアカウントと自分のワークスペースに対して Rayfin を実行できるか確認して。デプロイはまだしないで。
```

🤖 **Copilot の動き**（`apps/taxi-insights` で実行）

```bash
python3 ../../scripts/rayfin_az.py up --dry-run --verbose
```

- Azure CLI のアカウント・テナント・ワークスペースを参加者設定と照合し、一致した場合だけ Rayfin を実行します。
- トークンは子プロセスの環境変数にだけ渡され、画面やファイルには出ません。

### ローカル PC の場合

🤖 **Copilot に入力**

```text
登録済みのテナントで rayfin login をして、サインインしたアカウントとテナントが参加者設定と一致するか確認して。
```

🙋 **あなたの操作**: 開いたブラウザで **登録済みのアカウント** を選んでサインインします。
ブラウザが開かない、または戻ってこない場合は、Codespaces と同じラッパーを使うよう Copilot に指示します。

✅ **期待する結果**: 自分のワークスペース（例: `student3`）が対象として表示される。

---

## 9-3. ダッシュボードを作る（セマンティックモデル）

🤖 **Copilot に入力**

```text
taxi-insights に「NYC Taxi Insights」ダッシュボードを作って。
データは自分のワークスペースの sm_taxi セマンティックモデルを Rayfin の connector で DAX 実行して取得して。
- KPI: 総トリップ数・売上合計・平均運賃・平均距離
- 乗車区別のトリップ数（横棒）と、時間帯別の平均運賃（縦棒）
- 乗車区を選ぶと、その区から降車区ごとのトリップ数を表示する
サンプルデータで代用せず、取得できない場合はエラーを画面に表示して。
```

🤖 **Copilot の動き**

- プロジェクトのスキルに従って connector と分析用の機能を追加し、`sm_taxi` の ID を API で特定して connector を登録します
  （`rayfin connector add` は認証が必要なため、Codespaces では `rayfin_az.py connector add ...` で実行）。
- セマンティックモデル connector は **delegated**（アプリを開いた人の権限）で `executeQuery` を実行します。
- DAX では Lab 05 のメジャー（`[Trips]`・`[Total Amount]`・`[Avg Fare]`・`[Avg Trip Distance]`）を使います。

---

## 9-4. 入力フォームを追加する（アプリのデータ）

🤖 **Copilot に入力**

```text
ゾーンにメモを残せる「ゾーンメモ」機能を追加して。
項目は乗車ゾーンの LocationID、タグ（混雑・空港・要注意 から選択）、本文（最大 500 文字）。
サインインしたユーザーは自分のメモだけを作成・表示・削除できるように権限を設定して。
一覧は新しい順に表示して。
```

🤖 **Copilot の動き**

- アプリのデータモデルにエンティティを追加し、**権限のデコレーターと行レベルの条件（自分の行だけ）** を必ず付けます
  （付け忘れると、サインインした全員が全件を操作できてしまうため）。
- 保存先はアプリ専用の Fabric SQL Database で、OneLake に自動でミラーされます。

---

## 9-5. Data Agent に質問できるチャットを追加する

🤖 **Copilot に入力**

```text
画面右下のボタンで開くチャットパネルを追加して、自分のワークスペースの公開済み Data Agent taxi_metrics_agent に質問できるようにして。
Rayfin Functions から Data Agent の MCP エンドポイントを呼ぶ方式にして、トークンはブラウザに渡さないで。
Agent の ID は API で調べて設定して。応答に数分かかる場合があることを画面に表示して。
教材の samples/rayfin の参照実装も確認して、内容が同じ方針になっているか比べて。
```

🤖 **Copilot の動き**

- Functions を追加し（`npm run pack:add -- functions`）、プロジェクトの `fabric-data-agent` スキルに従って実装します。
- 参照実装: [`samples/rayfin/functions/`](../samples/rayfin/functions/)（ローカルのモックで MCP の手順・SSE 応答を検証済み）
  - `ctx.Tokens.Fabric`（アプリ所有者の権限）で `initialize` → `tools/list` → `tools/call` を実行
  - 質問は 500 文字以内、回答は 4,000 文字以内に制限し、質問・回答・トークンをログに出さない
- 型の生成は `npx rayfin functions init` の再実行で行います（Functions の Core Tools は不要）。

---

## 9-6. 公開する

🤖 **Copilot に入力**

```text
taxi-insights をビルドして型チェックが通ることを確認してから、自分のワークスペースに公開して。
Codespaces なら教材の Rayfin 認証ラッパーを使って。公開後にデプロイ状態を確認して、公開 URL を教えて。
```

🤖 **Copilot の動き**（Codespaces の例）

```bash
npm run typecheck && npm run build
python3 ../../scripts/rayfin_az.py up --yes
python3 ../../scripts/rayfin_az.py up status
```

✅ **期待する結果**: `taxi-insights` が自分のワークスペースに作成され、`*.webapp.fabricapps.net` の公開 URL が表示される。

---

## 9-7. ブラウザで動作を確認する

🌐 **ブラウザ**

1. 公開 URL を **InPrivate / シークレットウィンドウ** で開きます。
2. 🙋 登録済みのアカウントでサインインします。
3. 次を確認します。

| 確認 | 期待する結果 |
|---|---|
| KPI | 37,948 件 / $687,602.60 / $11.92 / 3.49 マイル |
| 乗車区の選択 | Manhattan を選ぶと、降車区 Brooklyn が 2,340 件 |
| ゾーンメモ | 1 件保存し、再読み込み後も残る |
| チャット | 「総トリップ数は？」に 37,948 件を含む回答 |

> [!WARNING]
> チャットは **アプリ所有者（あなた）の権限** で Data Agent を呼び出します。アプリを他の人と共有すると、
> その人はあなたが読めるデータについて質問できるようになります。共有する前に回答してよい範囲か確認してください。

---

## ✅ チェックポイント

- [ ] `apps/taxi-insights` を作成し、ビルドと型チェックが成功した
- [ ] トークンを表示・保存せずにデプロイできた
- [ ] ブラウザでダッシュボード・ゾーンメモ・チャットが動作した

## 🧹 トラブルシュート

| 症状 | 🤖 Copilot に入力 |
|---|---|
| `rayfin login` が戻ってこない | 「rayfin login を止めて、教材の Rayfin 認証ラッパーで実行し直して」 |
| `アカウントまたはテナントが一致しません` | 「Azure CLI を登録済みのアカウントでサインインし直してから、もう一度実行して」 |
| しばらくして認証エラー | 同じコマンドを再実行（トークンを取り直す） |
| ダッシュボードが 401/403 | 「sm_taxi に対する私の権限と、connector の設定を確認して」 |
| 画面が白い | 「ブラウザのコンソールエラーと rayfin up status を確認して原因を教えて」 |
| チャットがタイムアウト | Agent の初回応答は遅いことがある。もう一度質問。続く場合は Lab 08 の `agent-ask` で Agent 単体を確認 |
| チャットが 403 | 「Agent が公開済みか、Function の Agent ID が正しいか確認して」 |

デザインを磨く場合は [任意 A](optional-a-ux.md)、Ontology を Foundry から使う場合は [任意 B](optional-b-foundry-ontology.md) へ進みます。
