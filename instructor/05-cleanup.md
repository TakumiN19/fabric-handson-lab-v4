# 講師ガイド 05 — 片付け

## 1. 受講者が作成したアイテムの削除

ハンズオンで作成したアイテム（`config/workshop.json` の名前と `nb_*` Notebook）だけを対象にします。
既定は計画表示のみです。内容を確認してから `--apply` を付けて実行してください。

```bash
python3 scripts/instructor/workspaces.py cleanup --from 1 --to 30            # 削除対象の確認
python3 scripts/instructor/workspaces.py cleanup --from 1 --to 30 --apply    # 削除
python3 scripts/instructor/workspaces.py cleanup --from 1 --to 30 --delete-workspaces --apply   # ワークスペースごと削除
```

Fabric App が作成した SQL Database などが名前の一致で消えない場合は、ポータルで残りを確認します。

## 2. 費用の停止

- [ ] Fabric 容量を一時停止またはスケールダウン
- [ ] 講師が Foundry（任意 B）を使った場合は、Foundry プロジェクト・検索リソースを停止または削除

## 3. 認証情報と共有

- [ ] 受講者アカウントのパスワードをリセット、または無効化
- [ ] 共有接続の受講者への共有を解除
- [ ] サービスプリンシパルのシークレットを失効（次回も使う場合はローテーション）
- [ ] 一時的に付与したライセンス・グループを解除

## 4. 次回への反映

リハーサル記録と当日の障害を [04](04-rehearsal-and-runbook.md) に残し、検証済みバージョン（`config/versions.env`）を更新する場合は
通しリハーサルをやり直してください。
