# ローカル PC での準備

Codespaces を使えない場合だけ実施します。バージョンは [`config/versions.env`](../config/versions.env) が基準です。
ここに書いた導入作業は、Copilot をインストールする前のため **⌨️ ターミナル** で実行します。

## 1. 教材を取得する

```bash
git clone https://github.com/TakumiN19/fabric-handson-lab-v4.git
cd fabric-handson-lab-v4
```

Git がない場合は、GitHub の **Code › Download ZIP** で取得して展開し、VS Code でフォルダーを開きます。

## 2. ツールを導入する

| ツール | Windows（PowerShell 7） | macOS（Homebrew） |
|---|---|---|
| Node.js 22 LTS | `winget install OpenJS.NodeJS.LTS` | [nodejs.org](https://nodejs.org/) の 22.x LTS インストーラー |
| Python 3.12 | `winget install Python.Python.3.12` | `brew install python@3.12` |
| Azure CLI | `winget install Microsoft.AzureCLI` | `brew install azure-cli` |
| GitHub Copilot CLI | `npm install -g @github/copilot` | `npm install -g @github/copilot` |
| go-sqlcmd（任意） | `winget install sqlcmd` | `brew install sqlcmd` |

導入後は VS Code を再起動し、新しいターミナルで確認します。

```bash
node --version
python3 --version      # Windows では python --version または py --version
az version
copilot --version
```

## 3. Copilot を起動して残りを任せる

```bash
copilot login
copilot
```

この後は [Lab 00 の 0-3](../labs/00-setup.md#0-3-環境を診断し足りないものを準備する) のプロンプトで、
プラグイン（`fabric-skills`、`powerbi-authoring`、`rayfin`）と npm の CLI を Copilot に導入してもらいます。

## Windows の注意

- 教材の補助コマンドは Python で書かれているため、PowerShell でもそのまま動きます（`python3` の代わりに `python` を使う場合があります）。
- Azure CLI は Windows の認証ブローカー（WAM）を使います。ウィンドウが表示されない場合は
  [認証のトラブルシュート](auth-troubleshooting.md) を参照してください。
