---
paths:
  - "**"
---

# APM パッケージとしての取り扱い

本ガードレール（機密情報の取り扱い・システム破壊防止・環境分離・拡張機能評価）は、[Microsoft APM (Agent Package Manager)](https://github.com/microsoft/apm) のパッケージ `qmonus/qmonus-ai-guardrails` として配布され、`apm.yml` / `apm.lock.yaml` で版管理されている。Agent はこのプロジェクトで作業するとき、本パッケージの取り扱いについて以下を前提に振る舞う。

## clone 後は必ず `apm install` を実行する

- `apm_modules/`（パッケージキャッシュ）は `.gitignore` 対象で**コミットされない**。`node_modules` と同じく、clone 後に各自が `apm install` で復元する。
- 展開先ファイル（`.claude/rules/*` / `.github/instructions/*`）はコミットされるため、ルール本体は install なしでも Agent に読まれる。ただし **instruction 間の相互参照リンクは install 時に `apm_modules/` 配下へ書き換えられる**ため、`apm install` を実行していない clone 環境ではそれらのリンクが解決しない。
- したがって、リポジトリを clone したら（または `apm.yml` に依存があるのに `apm_modules/` が無ければ）、Agent は **`apm install`（harness 未検出なら `--target` 指定）**の実行を提案する。

## 更新の方法

- 別バージョンへ上げる: `apm.yml` のピン（例 `#v0.1.0`）を書き換えてから `apm update`（CI では `apm update --yes`）。
- 現在のピン範囲内で最新参照に追従: `apm update`。
- CI で lock との整合を強制したい場合: `apm install --frozen`（lock と `apm.yml` が不整合なら install を拒否する）。
- ガードレール本体（ルール文面）の変更は全プロジェクトの Agent 挙動に影響するため、**本番コードと同等のレビュー（PR で差分確認）**を経て取り込む。自動マージはしない。

## 推奨 apm CLI バージョン

- **0.23.0 以上**を推奨。少なくとも、パッケージ内相対リンクの書き換えが導入された **0.12.3 以上**が必要（それ未満では展開ファイル内の相互参照が壊れる）。
- バージョンは `apm --version` で確認する。

## 禁止・確認の継承

- 本パッケージの配布物（`.claude/rules/*` / `.github/instructions/*` / `apm.yml` / `apm.lock.yaml`）は Agent 挙動のベースライン。これらの変更は、CI/CD 設定変更や `.gitignore` 編集と同様に**確認必須**として扱う（システム破壊防止ルールの Git カテゴリに準ずる）。
- `apm_modules/` を `.gitignore` から外してコミットする運用は推奨しない（キャッシュは各自 install で復元する前提）。

## プロジェクト固有のオーバーライド

ピンの追従ポリシー（タグ固定追従かブランチ追従か）、更新を自動 PR 化するか、CI に `apm audit` / `--frozen` をどう組み込むかは、各プロジェクトで定義する。詳細な導入・運用手順は本パッケージの [利用ガイド](https://github.com/qmonus/qmonus-ai-guardrails/blob/v1.1.0/docs/usage.md) を参照する。
