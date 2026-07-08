#!/usr/bin/env python3
"""endoflife.date を使い、Python本体とDockerfileの公式ベースイメージのEOL状況を確認する。"""
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

# os.walk で再帰しないディレクトリ名（依存キャッシュ配下のDockerfileは対象外）。
EXCLUDED_DIR_NAMES = {"node_modules", ".venv", "venv", "site-packages", "apm_modules"}
PRUNED_DIR_NAMES = EXCLUDED_DIR_NAMES | {".git"}

FROM_RE = re.compile(r"^\s*FROM\s+(?:--platform=\S+\s+)?(\S+)(?:\s+[Aa][Ss]\s+(\S+))?", re.MULTILINE)
ARG_RE = re.compile(r"^\s*ARG\s+([A-Za-z_][A-Za-z0-9_]*)(?:=(\S+))?", re.MULTILINE)
VAR_RE = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?")

DEBIAN_CODENAMES = {"stretch", "buster", "bullseye", "bookworm", "trixie", "sid"}

# Docker公式の「言語」イメージ名 -> (endoflife.date product, タグからバージョンを取り出す正規表現)
LANGUAGE_PRODUCTS = {
    "python": ("python", re.compile(r"^([0-9]+\.[0-9]+)")),
    "node": ("nodejs", re.compile(r"^([0-9]+)")),
    "golang": ("go", re.compile(r"^([0-9]+\.[0-9]+)")),
}

# Docker公式の「OS」イメージ名 -> (endoflife.date product, タグからバージョンを取り出す正規表現)
OS_PRODUCTS = {
    "debian": ("debian", re.compile(r"^([0-9]+)")),
    "ubuntu": ("ubuntu", re.compile(r"^([0-9]+\.[0-9]+)")),
    "alpine": ("alpine", re.compile(r"^([0-9]+\.[0-9]+)")),
    "almalinux": ("almalinux", re.compile(r"^([0-9]+)")),
    "centos": ("centos", re.compile(r"^([0-9]+)")),
}

PRODUCT_LABELS = {
    "python": "Python",
    "nodejs": "Node.js",
    "go": "Go",
    "debian": "Debian",
    "ubuntu": "Ubuntu",
    "alpine": "Alpine",
    "almalinux": "AlmaLinux",
    "centos": "CentOS",
}


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=10) as res:
        return json.load(res)


def parse_pyproject_python(path):
    text = path.read_text()
    m = re.search(r'^python\s*=\s*"[~^]?([0-9]+\.[0-9]+)', text, re.MULTILINE)
    return m.group(1) if m else None


def find_dockerfiles():
    found = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in PRUNED_DIR_NAMES]
        for filename in filenames:
            if filename.lower().startswith("dockerfile"):
                found.append(Path(dirpath) / filename)
    return sorted(found)


def resolve_arg_defaults(text):
    # `ARG NAME=default` のデフォルト値のみを解決する。--build-arg で渡される値までは追わない。
    return {name: default.strip("\"'") for name, default in ARG_RE.findall(text) if default}


def substitute_vars(ref, args):
    return VAR_RE.sub(lambda m: args.get(m.group(1), m.group(0)), ref)


def parse_image_ref(image_ref):
    ref = image_ref.split("@", 1)[0]  # digest指定 (name:tag@sha256:...) を除く
    if "$" in ref:
        return None  # ARGにデフォルト値がなく解決できない
    basename = ref.rsplit("/", 1)[-1]  # レジストリ/パス部分を除いた末尾のイメージ名
    if ":" not in basename:
        return None  # タグ省略(=latest)はバージョン不明のため対象外
    name, tag = basename.split(":", 1)
    if not tag:
        return None
    return name.lower(), tag


def find_debian_codename_in_tag(tag):
    for token in re.split(r"[-_.]", tag.lower()):
        if token in DEBIAN_CODENAMES:
            return token
    return None


def base_image_targets(name, tag):
    # 戻り値: (product, cycle_or_codename, is_codename) のリスト
    targets = []
    if name in LANGUAGE_PRODUCTS:
        product, version_re = LANGUAGE_PRODUCTS[name]
        m = version_re.match(tag)
        if m:
            targets.append((product, m.group(1), False))
        codename = find_debian_codename_in_tag(tag)
        if codename:
            targets.append(("debian", codename, True))
    elif name in OS_PRODUCTS:
        product, version_re = OS_PRODUCTS[name]
        m = version_re.match(tag)
        if m:
            targets.append((product, m.group(1), False))
    return targets


def parse_dockerfile_targets(path):
    text = path.read_text()
    args = resolve_arg_defaults(text)

    targets = []
    stage_aliases = set()
    for raw_ref, alias in FROM_RE.findall(text):
        image_ref = substitute_vars(raw_ref, args)
        if image_ref in stage_aliases:
            continue  # 前段のビルドステージを参照しているだけで外部イメージではない
        if alias:
            stage_aliases.add(alias)

        parsed = parse_image_ref(image_ref)
        if not parsed:
            continue
        name, tag = parsed
        targets.extend(base_image_targets(name, tag))

    return targets


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

    pyproject_path = REPO_ROOT / "pyproject.toml"
    if pyproject_path.exists():
        pyproject_version = parse_pyproject_python(pyproject_path)
        if pyproject_version:
            targets.append(("pyproject.toml", "python", pyproject_version, False))

    for dockerfile in find_dockerfiles():
        rel = str(dockerfile.relative_to(REPO_ROOT))
        for product, version, is_codename in parse_dockerfile_targets(dockerfile):
            targets.append((rel, product, version, is_codename))

    return targets


def main():
    targets = collect_targets()
    product_cache = {}

    rows = []
    has_eol = False
    for source, product, version, is_codename in targets:
        if product not in product_cache:
            product_cache[product] = fetch_json(f"{ENDOFLIFE_API}/{product}.json")
        entries = product_cache[product]

        if is_codename:
            entry = find_debian_cycle_by_codename(entries, version)
            label = f"Debian ({version})"
        else:
            entry = find_cycle(entries, version)
            label = f"{PRODUCT_LABELS.get(product, product.capitalize())} {version}"

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
