# 認証のトラブルシュート

サインインでつまずきやすい箇所を、認証先ごとにまとめています。
**パスワード・MFA・アカウント選択・同意は必ず本人が行います。** 条件付きアクセスや MFA を回避する方法は使いません。

## どの認証で止まっているか

| 認証先 | 使う場面 | 確認方法（🤖 Copilot に入力） |
|---|---|---|
| GitHub（Copilot CLI） | Copilot の起動 | Copilot が起動しない場合は ⌨️ `copilot login` |
| Azure CLI | Copilot による Fabric 操作（Lab 01〜09） | 「Azure CLI のサインイン状態を確認して」 |
| Fabric ポータル | ブラウザで成果物を確認 | 🌐 右上のアカウント表示 |
| Rayfin CLI | アプリの作成・公開（Lab 09） | 「Rayfin の認証状態を確認して」 |
| 公開アプリ | アプリの利用（Lab 09） | 🌐 公開 URL でサインイン |

## 方式の選び方

| 環境 | GitHub Copilot | Azure CLI | Rayfin CLI |
|---|---|---|---|
| Codespaces | デバイスコード（既定） | デバイスコード | `scripts/rayfin_az.py`（Azure CLI のサインインを利用） |
| ローカル PC（Windows） | ブラウザ | ブラウザ（WAM）→ だめならデバイスコード | `rayfin login` → だめならラッパー |
| ローカル PC（macOS / Linux） | ブラウザ | ブラウザ → だめならデバイスコード | `rayfin login` → だめならラッパー |
| SSH・リモートデスクトップ | デバイスコード | デバイスコード | ラッパー |

> デバイスコード方式は「ブラウザが不要になる方式」ではありません。表示された URL を、別のブラウザ（手元の PC やスマートフォン）で開いて本人が認証します。

## よくある症状

| 症状 | 原因 | 対処 |
|---|---|---|
| 会社・個人のアカウントが自動で選ばれる | ブラウザに既存のサインインがある | InPrivate / シークレットウィンドウでコードを入力。「別のアカウントを使用」 |
| `No subscriptions found` | 受講者アカウントに Azure サブスクリプションがない | `--allow-no-subscriptions` を付けて再サインイン（正常な状態） |
| コードの期限切れ | 約 15 分で失効 | 同じプロンプトを再送して新しいコードを取得 |
| `AADSTS50076` / `AADSTS50079` | MFA の登録・応答が必要 | 画面の指示に従い MFA を完了。登録できない場合は講師へ |
| `AADSTS53003` など条件付きアクセス | デバイスや場所がポリシーで拒否 | **回避しない**。講師・管理者へ（デバイスコードの許可などは管理者の判断） |
| Windows で `User cancelled the Accounts Control Operation` | WAM（Windows の認証ブローカー）の問題 | 「Azure CLI のブラウザ認証に切り替えてサインインして」→ `az config set core.enable_broker_on_windows=false` |
| Edge で `This connection isn't secure` | localhost の HSTS 設定 | `edge://net-internals/#hsts` で `localhost` を削除、またはデバイスコード方式 |
| `rayfin login` がブラウザ認証後に戻らない | 戻り先（コンテナー内の localhost）に届かない | 「教材の Rayfin 認証ラッパーで実行して」 |
| Rayfin でキーチェーンのエラー | OS のキーチェーンがない環境 | ラッパーを使う（トークンを保存しない）。`--encryption-fallback-enabled` は平文保存になるため使わない |
| 数十分後に 401 | アクセストークンの期限切れ（約 1 時間） | 同じ操作を再実行（Azure CLI が自動で取り直す） |
| 別の参加者のワークスペースが操作対象になりそう | 参加者設定またはサインインの取り違え | `lab.py check` が止めるので、表示された理由に従って登録・サインインをやり直す |

## サインインし直す

🤖 **Copilot に入力**

```text
Azure CLI からサインアウトして、登録済みのアカウントとテナントでデバイスコード方式でサインインし直して。
その後、lab.py check で一致を確認して。
```

認証キャッシュを丸ごと削除する操作（`~/.azure` の削除など）は、ほかの環境にも影響するため標準手順にしていません。
