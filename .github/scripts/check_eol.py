#!/usr/bin/env python3
"""endoflife.date を使い、Python本体とDockerfileのDebianベースイメージのEOL状況を確認する。"""
import datetime
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENDOFLIFE_API = "https://endoflife.date/api"
WARN_WITHIN_DAYS = 90


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=10) as res:
        return json.load(res)


def parse_pyproject_python(path):
    text = path.read_text()
    m = re.search(r'^python\s*=\s*"[~^]?([0-9]+\.[0-9]+)', text, re.MULTILINE)
    return m.group(1) if m else None


def parse_dockerfile_base_images(path):
    text = path.read_text()
    return re.findall(r"FROM\s+python:([0-9]+\.[0-9]+)-slim-([a-z]+)", text)


def find_cycle(entries, cycle):
    return next((e for e in entries if e.get("cycle") == cycle), None)


def find_debian_cycle_by_codename(entries, codename):
    return next(
        (e for e in entries if str(e.get("codename", "")).lower() == codename.lower()),
        None,
    )


def eol_status(eol_value):
    if not eol_value:
        return "unknown", None
    eol_date = datetime.date.fromisoformat(eol_value)
    days_left = (eol_date - datetime.date.today()).days
    if days_left < 0:
        return "EOL済み", eol_date
    if days_left <= WARN_WITHIN_DAYS:
        return f"まもなくEOL(残{days_left}日)", eol_date
    return "サポート中", eol_date


def collect_targets():
    targets = []

    pyproject_version = parse_pyproject_python(REPO_ROOT / "pyproject.toml")
    if pyproject_version:
        targets.append(("pyproject.toml", "python", pyproject_version))

    for dockerfile in sorted(REPO_ROOT.glob("build/**/Dockerfile*")):
        rel = str(dockerfile.relative_to(REPO_ROOT))
        for py_version, codename in parse_dockerfile_base_images(dockerfile):
            targets.append((rel, "python", py_version))
            targets.append((rel, "debian", codename))

    return targets


def main():
    targets = collect_targets()
    product_cache = {}

    rows = []
    has_eol = False
    for source, product, version in targets:
        if product not in product_cache:
            product_cache[product] = fetch_json(f"{ENDOFLIFE_API}/{product}.json")
        entries = product_cache[product]

        if product == "debian":
            entry = find_debian_cycle_by_codename(entries, version)
            label = f"Debian ({version})"
        else:
            entry = find_cycle(entries, version)
            label = f"Python {version}"

        if entry is None:
            rows.append((source, label, "-", "-", "⚠️ endoflife.dateに情報なし"))
            continue

        cycle = entry.get("cycle", "-")
        status, eol_date = eol_status(entry.get("eol"))
        eol_date_str = eol_date.isoformat() if eol_date else "未定/なし"
        if status == "EOL済み":
            has_eol = True
            icon = "🔴"
        elif status.startswith("まもなく"):
            icon = "🟡"
        elif status == "unknown":
            icon = "⚪"
        else:
            icon = "🟢"
        rows.append((source, label, cycle, eol_date_str, f"{icon} {status}"))

    lines = [
        "## EOL Check (endoflife.date)",
        "",
        "| 検出元 | 対象 | サイクル | EOL日 | 状態 |",
        "|---|---|---|---|---|",
    ]
    for source, label, cycle, eol_date_str, status in rows:
        lines.append(f"| {source} | {label} | {cycle} | {eol_date_str} | {status} |")
    summary = "\n".join(lines)

    print(summary)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write(summary + "\n")

    if has_eol:
        print("::warning::EOLを迎えているモジュール/OSが検出されました。Job Summaryを確認してください。")


if __name__ == "__main__":
    sys.exit(main())
