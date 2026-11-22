#!/usr/bin/env python3
"""Read-only environment check for Lab V4.

It never installs, removes or changes anything and never prints tokens.
Copilot runs it in Lab 00 and turns each WARN/FAIL into the next action.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
results: list[tuple[str, str, str]] = []


def versions() -> dict[str, str]:
    values = {}
    for line in (ROOT / "config" / "versions.env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def run(*args: str) -> str:
    exe = shutil.which(args[0]) or shutil.which(args[0] + ".cmd")
    if not exe:
        return ""
    try:
        out = subprocess.run([exe, *args[1:]], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return (out.stdout or "") + (out.stderr or "")


def add(status: str, name: str, detail: str) -> None:
    results.append((status, name, detail))


def version_of(text: str) -> str:
    match = re.search(r"(\d+\.\d+\.\d+(?:-\d+)?)", text)
    return match.group(1) if match else ""


def main() -> int:
    pins = versions()
    tools = [
        ("node", ["node", "--version"], "NODE_VERSION", "Node.js 22 LTS 以上"),
        ("npm", ["npm", "--version"], "NPM_VERSION", None),
        ("az", ["az", "version", "-o", "json"], "AZURE_CLI_VERSION", "Azure CLI"),
        ("copilot", ["copilot", "--version"], "COPILOT_CLI_VERSION", "GitHub Copilot CLI"),
        ("python", [sys.executable, "--version"], "PYTHON_VERSION", None),
        ("sqlcmd", ["sqlcmd", "--version"], "SQLCMD_VERSION", "go-sqlcmd（任意: Lab 04 の手動確認用）"),
        ("powerbi-report-author", ["powerbi-report-author", "--version"], "POWERBI_AUTHORING_CLI_VERSION", "Power BI レポート作成 CLI（Lab 06）"),
    ]
    for name, command, pin, label in tools:
        output = run(*command)
        if name == "az" and output:
            try:
                output = json.loads(output).get("azure-cli", "")
            except ValueError:
                pass
        found = version_of(output)
        expected = pins.get(pin, "")
        if not found:
            add("FAIL" if name in ("node", "az", "copilot") else "WARN", name, f"未導入です（{label or name}）")
        elif found == expected.split("-")[0] or found == expected or (name == "node" and found.split(".")[0] in ("22", "24")):
            add("OK", name, found)
        else:
            add("WARN", name, f"{found}（検証済み: {expected}）")

    plugins = run("copilot", "plugin", "list")
    if plugins:
        def enabled(name: str) -> bool:
            line = next((l for l in plugins.splitlines() if f"{name}@" in l), "")
            return bool(line) and "[disabled]" not in line and "(disabled)" not in line
        for plugin, purpose in [("fabric-skills", "Fabric 操作"), ("powerbi-authoring", "Lab 06 レポート"), ("rayfin", "Lab 09 アプリ")]:
            add("OK" if enabled(plugin) else "FAIL", f"plugin:{plugin}", "有効" if enabled(plugin) else f"未導入または無効（{purpose}）")
        for alias in ("skills-for-fabric", "fabric-authoring", "fabric-consumption", "fabric-operations"):
            if enabled(alias):
                add("WARN", f"plugin:{alias}", "非推奨の別名です。fabric-skills と MCP が重複するため無効化を推奨")
        version_line = next((l for l in plugins.splitlines() if "fabric-skills@" in l), "")
        if version_line and pins.get("FABRIC_SKILLS_VERSION", "") not in version_line:
            add("WARN", "plugin:fabric-skills-version", f"{version_line.strip()}（検証済み: v{pins.get('FABRIC_SKILLS_VERSION')}）")
    else:
        add("FAIL", "plugins", "copilot plugin list を実行できません（Copilot CLI 未導入または未ログイン）")

    account = run("az", "account", "show", "-o", "json")
    try:
        data = json.loads(account)
        add("OK", "azure-login", f"{data.get('user', {}).get('name')} / {data.get('tenantId')}")
    except ValueError:
        add("WARN", "azure-login", "未サインイン（Lab 01 で実施）")

    student = ROOT / ".github" / "student.local.md"
    add("OK" if student.exists() else "WARN", "student", "登録済み" if student.exists() else "未登録（Lab 00 の 0-5 で登録）")

    width = max(len(name) for _, name, _ in results)
    for status, name, detail in results:
        print(f"[{status:4}] {name:<{width}}  {detail}")
    failed = [r for r in results if r[0] == "FAIL"]
    print(f"\n{len(results)} checks: {len(failed)} FAIL, {sum(r[0] == 'WARN' for r in results)} WARN")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
