# Lab 01 — サインインと接続確認

所要時間: 約 15 分　／　前提: [Lab 00](00-setup.md) で student 番号を登録済み

このラボでは、Azure CLI（Copilot が Fabric を操作するための認証）と Fabric ポータル（ブラウザで成果物を確認するための認証）に、
登録済みのアカウントでサインインします。

| サインイン先 | 用途 | 方式 |
|---|---|---|
| Azure CLI | Copilot が API・Notebook を操作する | デバイスコード（Codespaces）／ブラウザ（ローカル PC） |
| Fabric ポータル | 作成したアイテムを目で確認する | ブラウザ |

---

## 1-1. Azure CLI にサインインする

🤖 **Copilot に入力**

```text
登録済みの自分のアカウントとテナントで Azure CLI にサインインして。
Codespaces やブラウザ認証が使いづらい環境なら、デバイスコード方式にして。
サブスクリプションがない受講者アカウントとして扱って。
パスワードやトークンは表示・保存しないで。
```

🤖 **Copilot の動き**

- 参加者設定からテナント ID を読み、次を実行します（Codespaces ではデバイスコード方式）。

  ```bash
  az login --tenant <テナント ID> --allow-no-subscriptions --use-device-code
  ```

- 画面に **URL と 9 桁程度のコード** を表示し、あなたの操作を待ちます。

🙋 **あなたの操作**

1. 🌐 表示された URL（`https://microsoft.com/devicelogin`）を **InPrivate / シークレットウィンドウ** で開きます。
2. コードを入力し、**Copilot が表示したアカウント**（例: `student3@...`）でサインインします。
3. 「Azure CLI にサインインしようとしていますか？」には **続行** を選びます。
4. 「このウィンドウを閉じてかまいません」と表示されたら Copilot に戻ります。

> [!TIP]
> 会社や個人のアカウントが自動で選ばれる場合は、InPrivate ウィンドウを使うか、「別のアカウントを使用」を選んでください。
> デバイスコードは約 15 分で失効します。期限が切れたら同じプロンプトをもう一度送ります。

---

## 1-2. 自分のワークスペースに接続できるか確認する

🤖 **Copilot に入力**

```text
Fabric に接続して、サインイン中のアカウント・テナントと自分のワークスペースが登録内容と一致するか確認して。
一致したら Workspace ID を保存して、ワークスペースのアイテムを一覧して。
```

🤖 **Copilot の動き**

- `python3 scripts/lab.py check --save` を実行します。
- アカウント・テナント・ワークスペース名が一致しない場合は、ここで止まり、理由を表示します。
- 一致した場合だけ、API で確認した Workspace ID を `.github/student.local.md` に保存します。

✅ **期待する結果**

```json
{
  "user": "student3@M365x43914722.onmicrosoft.com",
  "tenant": "e6c1292e-65b7-4e2d-9e1b-13f24e7753fd",
  "workspace": "student3",
  "workspaceId": "（API で確認した ID）",
  "workspaceIdSaved": true,
  "items": []
}
```

ワークスペースが空でも問題ありません。Lab 02 以降でアイテムを作成していきます。

---

## 1-3. Fabric ポータルにサインインする

🌐 **ブラウザ**

1. **InPrivate / シークレットウィンドウ**で `https://app.fabric.microsoft.com` を開きます。
2. 🙋 Copilot が表示したアカウントでサインインします（詳しくは [Fabric ポータルへのサインイン](fabric-portal-login.md)）。
3. 左の **ワークスペース** から自分のワークスペース（例: `student3`）を開けることを確認します。

> [!IMPORTANT]
> Lab 05・06（Power BI）で Pro / PPU 相当のライセンスが必要です。講師から指示があった場合は、
> 右上のプロフィールから **Power BI の無料試用版** を開始してください。
> ワークスペースは講師の有料容量上に置いたままにし、Fabric の試用容量へ移動しないでください。

---

## ✅ チェックポイント

- [ ] Azure CLI に登録済みのアカウントでサインインした
- [ ] `lab.py check` でアカウント・テナント・ワークスペースが一致し、Workspace ID が保存された
- [ ] Fabric ポータルで自分のワークスペースを開けた

## 🧹 トラブルシュート

| 症状 | 🤖 Copilot に入力 |
|---|---|
| 別のアカウントでサインインしている | 「Azure CLI をサインアウトして、登録済みのアカウントでデバイスコード方式でサインインし直して」 |
| ブラウザが開かない・リモート環境 | 「デバイスコード方式でサインインして」 |
| `No subscriptions found` | 「サブスクリプションなしのテナントとしてサインインし直して」 |
| `AADSTS50076` などの MFA・条件付きアクセスのエラー | 回避せず講師に連絡（[認証トラブルシュート](../reference/auth-troubleshooting.md)） |
| ワークスペースが見つからない | 「今アクセスできるワークスペースを一覧して」で確認し、講師に連絡 |

次は **[Lab 02 — Notebook で取り込み・加工・検証](02-notebook-ingest-transform.md)** です。
