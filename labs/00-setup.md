# Lab 00 — 環境の準備と参加者登録

所要時間: 約 15 分　／　前提: 講師から student 番号とパスワードを受け取っていること

このラボでは、Copilot CLI を起動して環境を診断し、自分の student 番号を **一度だけ** 登録します。
ターミナルにコマンドを入力するのは、このラボの最初の 2 回だけです。以降はすべて Copilot に日本語で指示します。

> [!TIP]
> ローカル PC で進める場合は、先に [reference/local-setup.md](../reference/local-setup.md) でツールを導入してから 0-2 へ進みます。

---

## 0-1. Codespace を作成する

🌐 **ブラウザ**

1. [README](../README.md) の **Open in GitHub Codespaces** を選択します。
2. **Create codespace** を選び、ターミナルに `Dev Container tool setup completed` と表示されるまで待ちます（初回は数分）。
3. 続けて環境診断の結果が表示されます。`FAIL` がなければ次に進みます。

---

## 0-2. Copilot CLI にサインインして起動する

⌨️ **ターミナル**（このラボで入力するコマンドはこの 2 つだけです）

```bash
copilot login
copilot
```

🙋 **あなたの操作**

1. `copilot login` を実行すると、コードと `https://github.com/login/device` が表示されます。
2. ブラウザでその URL を開き、コードを入力して **ハンズオンで使う GitHub アカウント** で承認します。
3. `copilot` を起動して「このフォルダーを信頼するか」を聞かれたら、**Yes** を選びます。

✅ **成功の目安**: Copilot の入力欄が表示される。

> ローカル PC では、`copilot login` がブラウザを自動で開きます。開かない場合は `copilot login --device-code` を使います。

---

## 0-3. 環境を診断し、足りないものを準備する

🤖 **Copilot に入力**

```text
この教材の Lab 00 を読んで、ハンズオンに必要な環境を確認して。
検証済みのバージョンに合わせて、不足しているツールとプラグインだけを導入して。
既存の設定は勝手に消さず、MCP の重複や、私が行う必要がある操作があれば教えて。
再起動が必要なら、再起動後にどこから再開すればよいかも教えて。
```

🤖 **Copilot の動き**

- `python3 scripts/doctor.py` で、ツール・プラグイン・サインイン状態を読み取り専用で確認します。
- Codespace では検証済みのツールが導入済みのため、通常は確認だけで終わります。
- 不足があれば、`config/versions.env` のバージョンに合わせて `copilot plugin install` や `npm install -g` を実行します。
  OS の管理者権限が必要な導入は、あなたに手順を案内します。

✅ **期待する結果**

```text
[OK  ] plugin:fabric-skills       有効
[OK  ] plugin:powerbi-authoring   有効
[OK  ] plugin:rayfin              有効
[WARN] azure-login                未サインイン（Lab 01 で実施）
[WARN] student                    未登録（Lab 00 の 0-5 で登録）
```

`azure-login` と `student` の `WARN` は、この後の手順で解消するため問題ありません。

> [!NOTE]
> `fabric-skills` と `powerbi-authoring` は同じ Power BI 用 MCP サーバーを定義しているため、
> 起動時に「also defined by plugin」という案内が 1 行表示されることがあります。動作に影響はありません。
> 非推奨の `skills-for-fabric` も有効になっている場合、診断で `WARN` になります。Copilot の案内に従って無効化してください。

---

## 0-4. プラグインを導入した場合は Copilot を再起動する

0-3 でプラグインを導入した場合だけ、Copilot に再起動を案内されます。

🤖 **Copilot に入力**

```text
再起動が必要か教えて。必要なら、再起動の方法と、再開後に入力するプロンプトを教えて。
```

🙋 **あなたの操作**: 案内に従って Copilot を終了し、同じフォルダーで `copilot` を起動し直します。

---

## 0-5. 自分の student 番号を一度だけ登録する

🤖 **Copilot に入力**（`<番号>` だけを自分の番号に置き換えます。先頭の 0 も配布された表記のまま）

```text
私の student 番号は <番号> です。
この番号を記憶して、以降の全 Lab で自分のアカウントとワークスペースに自動で反映してください。
```

🤖 **Copilot の動き**

- 教材の共通指示（`.github/copilot-instructions.md`）に従い、番号からアカウント名とワークスペース名を生成します。
- `.github/student.local.md` に保存し、読み直して内容を表示します。
- この時点では Azure / Fabric へのサインインはしません。

✅ **期待する結果**（番号が 3 の場合）

```text
- student 番号: 3
- アカウント: student3@M365x43914722.onmicrosoft.com
- ワークスペース名: student3
- テナント ID: e6c1292e-65b7-4e2d-9e1b-13f24e7753fd
```

**表示されたアカウントが配布されたものと一致すること** を確認してください。

> [!IMPORTANT]
> `.github/student.local.md` はこのフォルダーにだけ保存され、Git にはコミットされません。
> 新しい Codespace や別の PC では、もう一度 0-5 を実行してください。

---

## ✅ チェックポイント

- [ ] Copilot CLI にサインインし、教材フォルダーで起動できた
- [ ] 環境診断で `FAIL` がない
- [ ] student 番号を登録し、表示されたアカウントが配布されたものと一致した

## 🧹 トラブルシュート

| 症状 | 🤖 Copilot に入力 |
|---|---|
| 番号を聞き直される | 「`.github/copilot-instructions.md` が読み込まれているか確認して」。読み込まれていなければ教材フォルダーで Copilot を起動し直す |
| プラグインが見つからない | 「Lab 00 の手順で fabric-skills と powerbi-authoring と rayfin を導入し直して」 |
| `copilot login` が進まない | ⌨️ `copilot login --device-code` を実行し、表示されたコードを 🌐 `https://github.com/login/device` に入力 |
| Copilot のライセンスエラー | 講師に連絡（組織のポリシーまたはライセンス付与） |

次は **[Lab 01 — サインインと接続確認](01-sign-in.md)** です。
