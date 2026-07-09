#!/usr/bin/env python3
"""deps.dev (OpenSSF Scorecard) を使い、依存パッケージのメンテナンス状況を確認する。

Python(pyproject.toml (Poetry の [tool.poetry.dependencies] または PEP 621 の
[project.dependencies]/uv 等) / requirements*.txt) / npm(package.json) / Go(go.mod) を対象に、
各パッケージのソースリポジトリに対する OpenSSF Scorecard の Maintained チェック結果を取得する。
ロックファイル(poetry.lock / uv.lock / package-lock.json / go.sum)が同じディレクトリに存在する
場合は、そちらを優先して読み、直接依存だけでなく間接依存も対象にする。ロックファイルが無い場合は
マニフェストの直接依存のみを対象にする(従来どおり)。
"""
import fnmatch
import json
import os
import re
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPS_DEV_API = "https://api.deps.dev/v3"
MAINTAINED_CHECK = "Maintained"
LOW_SCORE_THRESHOLD = 3
# ロックファイル由来で依存数が数百〜千件規模になり得るため、デフォルトは低めにして
# deps.dev のレート制限を避ける。必要に応じて環境変数で調整できる。
MAX_WORKERS = int(os.environ.get("DEPS_DEV_MAX_WORKERS", "4"))
STATUS_PRIORITY = {"🔴": 0, "🟡": 1, "⚪": 2, "🟢": 3}

GO_REQUIRE_LINE = re.compile(r"^([^\s]+)\s+v[0-9][^\s]*(\s+//\s*indirect)?$")
REQUIREMENTS_NAME = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)")
# cue.mod は CUE言語のモジュールキャッシュ(node_modules相当)。配下の go.mod 等は
# ベンダーされた第三者モジュール自身のものでこのプロジェクトの直接依存ではないため除外する。
EXCLUDED_DIR_NAMES = {"node_modules", ".venv", "venv", "site-packages", "cue.mod"}
# os.walk で再帰しないディレクトリ。EXCLUDED_DIR_NAMES に加え、依存探索に無関係な .git も剪定する。
PRUNED_DIR_NAMES = EXCLUDED_DIR_NAMES | {".git"}


def is_excluded(path):
    return any(part in EXCLUDED_DIR_NAMES for part in path.parts)


def fetch_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        # 404/400 は「deps.devに未登録のパッケージ/バージョン」という想定内の結果であり、
        # ロックファイルで間接依存まで対象にすると頻発するため warning としては出さない。
        # それ以外のHTTPエラー(5xx等)は異常なので warning を出す。
        if e.code not in (400, 404):
            print(f"::warning::{url} の取得に失敗しました: HTTP {e.code}")
        return None
    except (OSError, json.JSONDecodeError) as e:
        # OSError は urllib.error.URLError の親クラスであり、生の
        # TimeoutError/ConnectionError 等も含めて捕捉できる。
        print(f"::warning::{url} の取得に失敗しました: {e}")
        return None


def normalize_pypi_name(name):
    # deps.dev の PyPI package id は正規化名(PEP 503)が前提になり得るため、小文字化して [-_.] を '-' に寄せる
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_pep621_requirement_name(requirement):
    # PEP 508 の依存指定文字列("fastmcp>=3.1.1,<4"等)から先頭のパッケージ名だけを取り出す。
    # requirements*.txt の行と同じ形なので REQUIREMENTS_NAME を再利用する。
    # "name @ url"(PEP 508 direct reference。VCS/URL/ローカルパス指定)は通常のPyPI名
    # 解決ができないため、requirements*.txt側のURL除外(「://」)と同様に対象外にする。
    requirement = requirement.strip()
    if "://" in requirement or " @ " in requirement:
        return None
    m = REQUIREMENTS_NAME.match(requirement)
    return m.group(1) if m else None


def parse_python_deps(path):
    # Poetry([tool.poetry.dependencies])と PEP 621([project.dependencies]、uv 等が使う形式)の
    # 両方を読み、和集合を返す。Poetry 2.x では [tool.poetry] と [project] が同じ
    # pyproject.toml に共存できるため、片方が存在すればもう片方を無視するのではなく
    # 両方解析して取りこぼしを防ぐ。
    with path.open("rb") as f:
        data = tomllib.load(f)

    names = []

    poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies")
    if poetry_deps is not None:
        names.extend(name for name in poetry_deps if name.lower() != "python")

    project = data.get("project", {})
    requirements = list(project.get("dependencies", []))
    for extra_requirements in project.get("optional-dependencies", {}).values():
        requirements.extend(extra_requirements)
    # PEP 735 の依存グループ([dependency-groups])。{"include-group": "..."} のような
    # 他グループ参照は文字列ではないため無視する。
    for group_entries in data.get("dependency-groups", {}).values():
        requirements.extend(entry for entry in group_entries if isinstance(entry, str))
    names.extend(n for n in (parse_pep621_requirement_name(req) for req in requirements) if n)

    return list(dict.fromkeys(normalize_pypi_name(n) for n in names))


def parse_pypi_lock_deps(path):
    # poetry.lock / uv.lock はいずれも解決済みの全パッケージを [[package]] (name/version)で
    # 列挙する同じ構造のため、共通のパーサーで扱える。直接/間接を問わず対象になる。
    with path.open("rb") as f:
        data = tomllib.load(f)
    names = [pkg["name"] for pkg in data.get("package", []) if pkg.get("name")]
    return [normalize_pypi_name(n) for n in names]


def parse_requirements_deps(path, *, _seen=None):
    if _seen is None:
        _seen = set()

    path = path.resolve()
    if is_excluded(path) or not path.is_relative_to(REPO_ROOT):
        return []
    if path in _seen or not path.is_file():
        return []
    _seen.add(path)

    names = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue

        # include: requirements の分割管理に対応（-rfile / -r file / --requirement=file 等）
        m_inc = re.match(r"^(?:-r|--requirement)(?:=|\s+)?(.+)$", line)
        if m_inc:
            inc = m_inc.group(1).strip()
            inc_path = (path.parent / inc).resolve()
            if is_excluded(inc_path) or not inc_path.is_relative_to(REPO_ROOT):
                continue
            names.extend(parse_requirements_deps(inc_path, _seen=_seen))
            continue

        # オプション行(-e/--index-url等)は除外
        if line.startswith("-"):
            continue

        # URL直接指定は通常のPyPI名解決ができないため除外
        if "://" in line:
            continue

        m = REQUIREMENTS_NAME.match(line)
        if m:
            names.append(normalize_pypi_name(m.group(1)))

    return list(dict.fromkeys(names))


NPM_DEPENDENCY_FIELDS = ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")


def parse_npm_deps(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    names = [name for field in NPM_DEPENDENCY_FIELDS for name in data.get(field, {})]
    return list(dict.fromkeys(names))


def parse_npm_lock_deps(path):
    # package-lock.json は解決済みの全パッケージ(直接/間接問わず)を列挙する。
    data = json.loads(path.read_text(encoding="utf-8"))
    names = set()

    packages = data.get("packages")
    if packages is not None:
        # lockfileVersion 2/3: キーはインストール先パス("", "node_modules/foo",
        # "node_modules/foo/node_modules/@scope/bar" 等)だが、npm workspaces では
        # "packages/foo" のような node_modules を含まないワークスペースパスも
        # 混在する。パッケージとして扱えるのは "node_modules/" を含むキーのみで、
        # 末尾の"node_modules/"以降がパッケージ名になる(スコープ付き名も保持される)。
        # ".bin"はシンボリックリンク置き場でパッケージ本体ではないため除外する。
        for key in packages:
            idx = key.rfind("node_modules/")
            if idx == -1:
                continue  # "" (プロジェクト自身) やワークスペースパスは対象外
            name = key[idx + len("node_modules/"):]
            if name and name != ".bin" and not name.startswith(".bin/"):
                names.add(name)
    else:
        # lockfileVersion 1: "dependencies" が {name: {dependencies: {...}}} の形でネストする。
        def walk(deps):
            for name, info in (deps or {}).items():
                names.add(name)
                walk((info or {}).get("dependencies"))

        walk(data.get("dependencies"))

    return sorted(names)


def parse_go_deps(path):
    text = path.read_text(encoding="utf-8")
    deps = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("require ("):
            in_block = True
            continue
        if in_block and stripped == ")":
            in_block = False
            continue
        # go.mod は require 行に任意コメントが付くため、コメントを分離して判定する
        code, _, comment = stripped.partition("//")
        is_indirect = comment.strip().startswith("indirect")
        if in_block:
            m = GO_REQUIRE_LINE.match(code.strip())
        elif code.strip().startswith("require "):
            m = GO_REQUIRE_LINE.match(code.strip()[len("require "):].strip())
        else:
            m = None
        if m and not is_indirect:  # "// indirect" は間接依存なので除外
            deps.append(m.group(1))
    return deps


GO_SUM_MODULE_RE = re.compile(r"^(\S+)\s+v\S+(?:/go\.mod)?\s+h1:")


def parse_go_sum_deps(path):
    # go.sum はビルドに使う全モジュール(直接/間接問わず)を列挙する。
    # 各モジュールは "module version h1:..." と "module version/go.mod h1:..." の2行で
    # 現れるため、モジュールパス単位で重複排除する。
    names = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = GO_SUM_MODULE_RE.match(line)
        if m:
            names.add(m.group(1))
    return sorted(names)


# (ファイル名パターン, deps.dev system, パーサー)
MANIFEST_MATCHERS = [
    ("requirements*.txt", "pypi", parse_requirements_deps),
    ("package.json", "npm", parse_npm_deps),
    ("go.mod", "go", parse_go_deps),
]

# マニフェストと同じディレクトリにロックファイルがあれば、そちらを優先する
# (ファイル名 -> (ロックファイル名, パーサー))。ロックファイルは直接/間接を問わず
# 解決済みの全パッケージを列挙するため、より網羅的な検出になる。
LOCK_OVERRIDES = {
    "package.json": ("package-lock.json", parse_npm_lock_deps),
    "go.mod": ("go.sum", parse_go_sum_deps),
}


def find_manifests():
    # os.walk は topdown=True がデフォルトで、dirnames をその場で書き換えれば配下を再帰しなくなる。
    # Path.glob("**/...") は除外ディレクトリの中身まで走査してから捨てるため、
    # node_modules/.venv 等が巨大な場合にI/Oコストが無視できない。os.walk側で剪定してから収集する。
    found = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in PRUNED_DIR_NAMES]
        for filename in filenames:
            for pattern, system, parser in MANIFEST_MATCHERS:
                if fnmatch.fnmatch(filename, pattern):
                    found.append((Path(dirpath) / filename, system, parser))
    return sorted(found, key=lambda item: str(item[0]))


def collect_targets():
    targets = []  # (source, deps_dev_system, package_name)

    pyproject = REPO_ROOT / "pyproject.toml"
    if pyproject.exists():
        # poetry.lock(Poetry) / uv.lock(uv) はいずれも [[package]] で解決済み全パッケージを
        # 列挙する同じ構造。どちらか存在する方を優先する。
        lock_path = next(
            (p for p in (pyproject.parent / "poetry.lock", pyproject.parent / "uv.lock") if p.exists()),
            None,
        )
        if lock_path:
            rel = str(lock_path.relative_to(REPO_ROOT))
            targets.extend((rel, "pypi", name) for name in parse_pypi_lock_deps(lock_path))
        else:
            rel = str(pyproject.relative_to(REPO_ROOT))
            targets.extend((rel, "pypi", name) for name in parse_python_deps(pyproject))

    for path, system, parser in find_manifests():
        lock_override = LOCK_OVERRIDES.get(path.name)
        lock_path = path.parent / lock_override[0] if lock_override else None
        if lock_path and lock_path.exists():
            rel = str(lock_path.relative_to(REPO_ROOT))
            targets.extend((rel, system, name) for name in lock_override[1](lock_path))
        else:
            rel = str(path.relative_to(REPO_ROOT))
            targets.extend((rel, system, name) for name in parser(path))

    return targets


def dedupe_targets(targets):
    # requirements*.txt を -r/--requirement で分割管理している場合に限らず、
    # 複数の依存定義ファイル（requirements/pyproject/package.json/go.mod 等）で同一パッケージが
    # 重複して検出されると deps.dev への問い合わせと出力が冗長になるため、(system, name) 単位で集約する。
    merged = {}
    for source, system, name in targets:
        key = (system, name)
        sources = merged.setdefault(key, [])
        if source not in sources:
            sources.append(source)
    return [(", ".join(sources), system, name) for (system, name), sources in merged.items()]


def resolve_source_project(system, name):
    encoded_name = urllib.parse.quote(name, safe="")
    pkg = fetch_json(f"{DEPS_DEV_API}/systems/{system}/packages/{encoded_name}")
    if not pkg or not pkg.get("versions"):
        return None, "deps.devからパッケージ情報を取得できず（未登録/404 または通信エラー）"
    version = next((v for v in pkg["versions"] if v.get("isDefault")), pkg["versions"][-1])
    version_str = urllib.parse.quote(version["versionKey"]["version"], safe="")

    ver_detail = fetch_json(f"{DEPS_DEV_API}/systems/{system}/packages/{encoded_name}/versions/{version_str}")
    if not ver_detail:
        return None, "バージョン情報の取得に失敗"

    source = next(
        (r for r in ver_detail.get("relatedProjects", []) if r.get("relationType") == "SOURCE_REPO"),
        None,
    )
    if not source:
        return None, "ソースリポジトリを特定できず"

    return source["projectKey"]["id"], None


def get_maintained_check(project_id):
    encoded_id = urllib.parse.quote(project_id, safe="")
    project = fetch_json(f"{DEPS_DEV_API}/projects/{encoded_id}")
    if not project or "scorecard" not in project:
        return None, "Scorecard情報を取得できませんでした（未登録または通信エラー）"

    check = next(
        (c for c in project["scorecard"].get("checks", []) if c.get("name") == MAINTAINED_CHECK),
        None,
    )
    if not check:
        return None, "Maintainedチェックなし"

    return check, None


def evaluate(target):
    source, system, name = target
    project_id, err = resolve_source_project(system, name)
    if err:
        return source, system, name, "-", "-", f"⚪ {err}"

    check, err = get_maintained_check(project_id)
    if err:
        return source, system, name, project_id, "-", f"⚪ {err}"

    score = check.get("score", -1)
    reason = check.get("reason") or "-"
    reason_lc = str(reason).lower()
    if "archived" in reason_lc:
        # archived は明示的な意思表示であり、直近コミット数ベースのスコアよりも信頼できるシグナル。
        # score(直近90日のコミット数ベース)だけで判定すると、枯れた安定パッケージまで
        # 誤検知するため(six, MarkupSafe等で実測済み)、archivedのみを致命的シグナルとして扱う。
        icon = "🔴"
    elif score < 0:
        icon = "⚪"
    elif score <= LOW_SCORE_THRESHOLD:
        icon = "🟡"
    else:
        icon = "🟢"

    return source, system, name, project_id, score, f"{icon} {reason}"


def write_summary(summary):
    print(summary)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(summary + "\n")


def main():
    targets = dedupe_targets(collect_targets())
    if not targets:
        write_summary(
            "## Dependency Maintenance Check (deps.dev / OpenSSF Scorecard)\n\n"
            "対象の依存パッケージが見つかりませんでした。"
        )
        return 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        rows = list(executor.map(evaluate, targets))

    rows.sort(key=lambda r: STATUS_PRIORITY.get(r[-1][0], 9))
    has_critical = any(row[-1].startswith("🔴") for row in rows)

    lines = [
        "## Dependency Maintenance Check (deps.dev / OpenSSF Scorecard)",
        "",
        "| 検出元 | エコシステム | パッケージ | ソースリポジトリ | Maintainedスコア | 状態 |",
        "|---|---|---|---|---|---|",
    ]
    for source, system, name, project_id, score, status in rows:
        lines.append(f"| {source} | {system} | {name} | {project_id} | {score} | {status} |")
    summary = "\n".join(lines)

    write_summary(summary)

    if has_critical:
        print("::warning::メンテナンスが停止している可能性のある依存パッケージが検出されました。Job Summaryを確認してください。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
