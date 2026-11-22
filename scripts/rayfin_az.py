#!/usr/bin/env python3
"""Run a Rayfin CLI command with the Azure CLI sign-in (Lab 09).

Why: in Codespaces and other remote terminals, `rayfin login` opens a browser
that must redirect back to a random localhost port inside the container. That
redirect often never arrives, so the CLI waits forever. Azure CLI device-code
sign-in works reliably there, and Rayfin officially accepts a Fabric token via
RAYFIN_TOKEN for pre-provisioned environments.

This wrapper:
  * verifies the signed-in account, tenant and workspace against the
    participant file (stops on any mismatch),
  * gets a short-lived Fabric token from Azure CLI,
  * passes it ONLY to the single child `npx rayfin ...` process,
  * never prints, logs or saves the token.

Usage (from the app folder):  python3 ../../scripts/rayfin_az.py up --yes
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab  # noqa: E402

ALLOWED = {"up", "dev", "connector", "functions", "login", "env", "docs", "init"}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] not in ALLOWED:
        print(f"ERROR: rayfin {argv[0]} はこのラッパーの対象外です。", file=sys.stderr)
        return 2
    if argv[0] == "login" and argv[1:2] != ["status"]:
        print("このラッパー経由ではブラウザのログインは不要です。`login status` で状態だけ確認できます。")
    try:
        fabric, workspace_id = lab.context()
        access_token = lab.token(lab.FABRIC_RESOURCE, fabric.tenant)
    except lab.LabError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        print("ERROR: npx が見つかりません。Node.js 22 以上を導入してください。", file=sys.stderr)
        return 1
    env = dict(os.environ)
    env.update({
        "RAYFIN_TOKEN": access_token,
        "RAYFIN_TENANT_ID": fabric.tenant,
        "RAYFIN_WORKSPACE_ID": workspace_id,
    })
    print(f"Rayfin を {fabric.student['account']} / ワークスペース {fabric.student['workspace']} で実行します。", file=sys.stderr)
    # Token is in the child environment only; it is not part of argv, so it never appears in process listings.
    completed = subprocess.run([npx, "rayfin", *argv], env=env)
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
