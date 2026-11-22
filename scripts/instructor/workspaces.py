#!/usr/bin/env python3
"""Instructor helper: provision, check and clean up participant workspaces.

Run with an instructor / Fabric admin Azure CLI sign-in. Every command is a dry
run unless --apply is given. Tokens are never printed.

  python3 scripts/instructor/workspaces.py provision --from 1 --to 30 --capacity "F32-handson"
  python3 scripts/instructor/workspaces.py preflight --from 1 --to 30
  python3 scripts/instructor/workspaces.py cleanup   --from 1 --to 30
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab  # noqa: E402

LAB_ITEM_TYPES = {"Lakehouse", "Warehouse", "Notebook", "SemanticModel", "Report", "Ontology", "DataAgent", "SQLEndpoint"}


def fabric_client() -> lab.Fabric:
    workshop = lab.load_workshop()
    account = lab.az_json("account", "show")
    if account.get("tenantId") != workshop["tenantId"]:
        raise lab.LabError("Azure CLI のテナントが config/workshop.json の tenantId と一致しません。")
    return lab.Fabric({"tenant": workshop["tenantId"], "workspace": "", "account": "", "number": "", "workspace_id": ""})


def participants(args: argparse.Namespace) -> list[tuple[str, str]]:
    workshop = lab.load_workshop()
    width = len(str(args.to)) if args.pad else 0
    result = []
    for number in range(args.start, args.to + 1):
        label = str(number).zfill(width) if width else str(number)
        result.append((f"{workshop['workspacePrefix']}{label}", f"{workshop['accountPrefix']}{label}@{workshop['accountDomain']}"))
    return result


def user_object_id(upn: str) -> str | None:
    result = subprocess.run(["az", "ad", "user", "show", "--id", upn, "--query", "id", "-o", "tsv", "--only-show-errors"],
                            capture_output=True, text=True)
    return result.stdout.strip() or None


def workspaces_by_name(fabric: lab.Fabric) -> dict[str, dict]:
    return {w["displayName"]: w for w in fabric.paged("/workspaces")}


def cmd_provision(args: argparse.Namespace) -> None:
    fabric = fabric_client()
    capacities = [c for c in fabric.paged("/capacities") if c.get("displayName") == args.capacity]
    if len(capacities) != 1:
        raise lab.LabError(f"容量 {args.capacity} を一意に特定できません。")
    capacity = capacities[0]
    if capacity.get("state") != "Active":
        raise lab.LabError(f"容量 {args.capacity} が Active ではありません（{capacity.get('state')}）。")
    existing = workspaces_by_name(fabric)
    for workspace_name, upn in participants(args):
        plan = []
        workspace = existing.get(workspace_name)
        if not workspace:
            plan.append("create workspace")
        elif workspace.get("capacityId") != capacity["id"]:
            plan.append("assign capacity")
        user_id = user_object_id(upn)
        if not user_id:
            print(f"[SKIP] {workspace_name}: ユーザー {upn} が見つかりません")
            continue
        plan.append(f"grant {args.role} to {upn}")
        print(f"[{'APPLY' if args.apply else 'PLAN '}] {workspace_name}: {', '.join(plan)}")
        if not args.apply:
            continue
        if not workspace:
            _, _, workspace = fabric.request("POST", "/workspaces", {"displayName": workspace_name, "capacityId": capacity["id"]})
        elif workspace.get("capacityId") != capacity["id"]:
            fabric.request("POST", f"/workspaces/{workspace['id']}/assignToCapacity", {"capacityId": capacity["id"]})
        roles = fabric.paged(f"/workspaces/{workspace['id']}/roleAssignments")
        if not any((r.get("principal") or {}).get("id") == user_id for r in roles):
            fabric.request("POST", f"/workspaces/{workspace['id']}/roleAssignments",
                           {"principal": {"id": user_id, "type": "User"}, "role": args.role})


def cmd_preflight(args: argparse.Namespace) -> None:
    fabric = fabric_client()
    workshop = lab.load_workshop()
    existing = workspaces_by_name(fabric)
    connections = [c for c in fabric.paged("/connections") if c.get("displayName") == workshop["sharedAdls"]["connectionName"]]
    connection_users: set[str] = set()
    if len(connections) == 1:
        for role in fabric.paged(f"/connections/{connections[0]['id']}/roleAssignments"):
            connection_users.add((role.get("principal") or {}).get("id", ""))
    print(f"共有接続 {workshop['sharedAdls']['connectionName']}: {'OK' if len(connections) == 1 else 'NOT FOUND / DUPLICATE'}")
    failures = 0
    for workspace_name, upn in participants(args):
        problems = []
        workspace = existing.get(workspace_name)
        user_id = user_object_id(upn)
        if not user_id:
            problems.append("ユーザーなし")
        if not workspace:
            problems.append("ワークスペースなし")
        else:
            _, _, details = fabric.request("GET", f"/workspaces/{workspace['id']}")
            if not details.get("capacityId"):
                problems.append("容量未割り当て")
            roles = {(r.get("principal") or {}).get("id"): r.get("role") for r in fabric.paged(f"/workspaces/{workspace['id']}/roleAssignments")}
            if user_id and roles.get(user_id) not in ("Admin", "Member", "Contributor"):
                problems.append(f"ロール不足（{roles.get(user_id)}）")
        if user_id and connections and user_id not in connection_users:
            problems.append("共有接続に未追加（グループ経由なら手動確認）")
        failures += bool(problems)
        print(f"[{'OK  ' if not problems else 'FAIL'}] {workspace_name} {upn} {'; '.join(problems)}")
    print(f"\n{failures} 件の要対応")


def cmd_cleanup(args: argparse.Namespace) -> None:
    fabric = fabric_client()
    workshop = lab.load_workshop()
    names = set(workshop["items"].values()) | set(lab.NOTEBOOKS)
    existing = workspaces_by_name(fabric)
    for workspace_name, _ in participants(args):
        workspace = existing.get(workspace_name)
        if not workspace:
            continue
        items = [i for i in fabric.paged(f"/workspaces/{workspace['id']}/items")
                 if i.get("displayName") in names and i.get("type") in LAB_ITEM_TYPES | {"AppBackend", "SQLDatabase"}]
        for item in items:
            print(f"[{'DELETE' if args.apply else 'PLAN  '}] {workspace_name}: {item['type']} {item['displayName']}")
            if args.apply and item["type"] != "SQLEndpoint":
                fabric.request("DELETE", f"/workspaces/{workspace['id']}/items/{item['id']}")
        if args.delete_workspaces:
            print(f"[{'DELETE' if args.apply else 'PLAN  '}] workspace {workspace_name}")
            if args.apply:
                fabric.request("DELETE", f"/workspaces/{workspace['id']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in [("provision", cmd_provision), ("preflight", cmd_preflight), ("cleanup", cmd_cleanup)]:
        command = sub.add_parser(name)
        command.add_argument("--from", dest="start", type=int, required=True)
        command.add_argument("--to", type=int, required=True)
        command.add_argument("--pad", action="store_true", help="Zero-pad numbers to the width of --to (e.g. student01)")
        command.set_defaults(func=func)
        if name != "preflight":
            command.add_argument("--apply", action="store_true", help="Actually make changes (default: plan only)")
        if name == "provision":
            command.add_argument("--capacity", required=True, help="Fabric capacity display name")
            command.add_argument("--role", default="Member", choices=["Member", "Contributor", "Admin"])
        if name == "cleanup":
            command.add_argument("--delete-workspaces", action="store_true")
    args = parser.parse_args()
    try:
        args.func(args)
    except lab.LabError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
