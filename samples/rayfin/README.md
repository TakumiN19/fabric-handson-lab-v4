# Rayfin 参照実装 — Data Agent を呼ぶ Function

Lab 09 のチャット機能の参照実装です。Rayfin 2.0.1 の `blankapp` テンプレートに Functions を追加し、
`npm run typecheck` と関数の型生成（`askDataAgent: { input: { question: string }; output: string }`）が成功することを確認しています。

| ファイル | 内容 |
|---|---|
| `functions/function_app.ts` | `askDataAgent` 関数。`AudienceType.Fabric` のトークン（アプリ所有者）で Data Agent の MCP を呼ぶ |
| `functions/data-agent-mcp.ts` | MCP（Streamable HTTP）の最小クライアント。`initialize` → `notifications/initialized` → `tools/list` → `tools/call` |
| `functions/agent-config.ts` | Workspace ID と Data Agent ID（Lab 09 で Copilot が API の結果から設定。秘密情報ではない） |
| `test/data-agent-mcp.test.mts` | ローカルのモック MCP サーバーでの検証（JSON・SSE 応答、セッション、エラー時に本文を漏らさない） |

## 方針

- トークンはサーバー側（Function）だけで使い、ブラウザ・ログ・戻り値に含めません。
- 質問は 500 文字、回答は 4,000 文字に制限します。Fabric の UDF ホストの上限（250 秒）より短い 240 秒で打ち切ります。
- MCP のツール名と質問の引数名は `tools/list` から取得し、ハードコードしません。
- プロジェクトの `.agents/skills/fabric-data-agent` スキル（Rayfin テンプレート同梱）と同じ方針です。
  Lab 09 では、Copilot がそのスキルに従って実装し、この参照実装と方針を比較します。

## テスト

```bash
cd samples/rayfin
npm test
```

Node.js 22.18 以上（TypeScript の型除去に対応）で実行できます。
