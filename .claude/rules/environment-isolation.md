---
paths:
  - "**"
---

# 環境分離

本インストラクションは、Coding Agent のプロンプト設定や deny 設定が原理的に迂回されうることを説明し、環境分離（Dev Container、Docker Sandbox、Agent 製品固有の sandbox 機能など）が必要となる条件と、Agent が環境分離前提の振る舞いで動くべき場面を定義する。

## なぜプロンプト設定と deny 設定だけでは不十分か

deny 設定は「Agent の直接ツール呼び出し」レイヤーでしか機能しない。Agent は以下の方法で制限を迂回できる：

### スクリプト経由の迂回

- `read(~/.aws/credentials)` を deny しても、`cat ~/.aws/credentials` を含むシェルスクリプトを書いて `bash` で実行すれば、同じ内容を取得できる
- `bash(aws ...)` を deny しても、同等の操作を行うスクリプトを生成・実行できる
- MCP Server や SKILL が配布するスクリプトを実行することで、スクリプト内部のコマンドが deny 設定の外で動作する

deny 設定は Agent が生成・実行するサブプロセスの中身までは制御しない。

### CLI ツールによる認証情報の透過的な利用

以下の CLI ツールは、ホストユーザーの認証情報をプロセス内部で直接読み取る。CLI 自体の実行を許可していれば、ファイルアクセス deny 設定があっても権限は透過的に使えてしまう：

- `git`（SSH 使用時の `~/.ssh/` 秘密鍵や `ssh-agent` の鍵でリモート push/pull）
- `gh`（`~/.config/gh/` のトークンでリポジトリ削除、設定変更、PR マージ、Actions Secret 操作、リリース作成）
- `aws`（`~/.aws/credentials` でクラウドリソースの作成・削除）
- `gcloud`（`~/.config/gcloud/` で同等操作）
- `az`（`~/.azure/` で同等操作）
- `ssh`（`~/.ssh/id_*` や `ssh-agent` の鍵でのリモート接続）
- `kubectl`（`~/.kube/config` による Kubernetes クラスタ操作）

## 環境分離が「必須」となる条件

以下に該当する場合、プロンプト設定と deny 設定のみに依存してはならない。環境分離を前提にする：

- 確認スキップオプション（Claude Code の `--dangerously-skip-permissions`、Copilot CLI の `--yolo` 等）を使用する場合
- 本番認証情報または商用環境（共有 dev/stg を含む、組織のクラウド・SaaS・リポジトリに到達できる認証情報）をローカル端末で扱う場合
- 信頼できないリポジトリ（外部コード、検証目的の他プロジェクトのクローン等）に対して作業する場合

## 環境分離が「推奨」となる条件

- 環境変数に dev/local 認証情報を保存して作業する場合
- 外部から取得したコード・依存の検証を行う場合
- MCP Server や SKILL の評価中で、信頼性が未確立な場合

## 環境分離の選択肢

| 手段 | 特徴 | 代表的な用途 |
| --- | --- | --- |
| Dev Container（プロジェクト・コンテナ） | プロジェクト単位のコンテナ。VS Code / Copilot / Claude Code と組み合わせやすい | 通常の開発で認証情報を扱う場合 |
| Docker Sandbox / microVM | ホストから強く分離。ファイルシステムとネットワークを厳格に制御 | 信頼できないコード、最大限のリスク低減 |
| Agent 製品固有の sandbox | Claude Code の `/sandbox` など製品組み込みの隔離機能 | 製品が提供する範囲で素早く隔離したいとき |
| MCP Server 個別 sandbox | VS Code 拡張版 Copilot で MCP Server 単体をサンドボックスで実行（macOS/Linux） | 信頼性未確立の MCP Server の評価時 |

## Agent が環境分離前提で振る舞うべき事項

Agent は、本パッケージをインストールしたプロジェクトでは以下を前提に動く：

1. ホスト認証情報（`~/.aws/`、`~/.ssh/`、`~/.config/gcloud/` 等）に触らない。触ろうとする操作を自ら提案した場合、環境分離の有無を利用者に確認する
2. 環境分離されていないと判断した場合、禁止操作（[system-safety.instructions.md](../../apm_modules/qmonus/qmonus-ai-guardrails/.apm/instructions/system-safety.instructions.md) 参照）の条件はより保守的に解釈する（例: プロジェクト外ファイルの読み取りも確認必須として扱う）
3. スクリプトを書いて deny 設定を迂回する行為はしない。deny されている直接呼び出しと、それを達成するスクリプトは同じ禁止対象である
4. 確認スキップオプションが有効になっていることに気付いた場合、環境分離の有無を確認する。環境分離されていないまま確認スキップで動くことを避ける

## 環境分離で緩和できる確認項目

環境分離によって技術的に不可能となっている操作については、プロンプト設定での重複確認を省略してよい。たとえば：

- プロジェクトディレクトリだけをマウントする Dev Container では、プロジェクト外ファイル操作は物理的に不可能 → 確認指示を省略できる
- 環境変数を継承しない設定であれば、環境変数アクセスの確認は不要

ただし、ネットワークアクセスや外部 API 呼び出しが残っている場合、それらは別途 [secrets-management.instructions.md](../../apm_modules/qmonus/qmonus-ai-guardrails/.apm/instructions/secrets-management.instructions.md) と [extension-evaluation.instructions.md](../../apm_modules/qmonus/qmonus-ai-guardrails/.apm/instructions/extension-evaluation.instructions.md) のルールを適用する。

## 外部サービス連携時の考慮

AWS CLI、GitHub CLI 等の外部サービス連携が多い作業では、環境分離に伴う設定コスト（認証情報の受け渡し、ネットワーク設定等）も考慮する。環境分離の選択肢が現実的でない場合は、専用クレデンシャル＋参照権限のみ、という [system-safety.instructions.md](../../apm_modules/qmonus/qmonus-ai-guardrails/.apm/instructions/system-safety.instructions.md) の推奨アプローチを採用する。

## プロジェクト固有のオーバーライド

本パッケージは環境分離の考え方と適用条件を定義するに留まる。具体的にどの分離手段を採用するか、どの認証情報フローを使うか、どのサンドボックス設定を標準とするかは、各プロジェクトで定義する。
