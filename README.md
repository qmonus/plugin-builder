[![CI](https://github.com/qmonus/plugin-builder/actions/workflows/ci.yml/badge.svg)](https://github.com/qmonus/plugin-builder/actions/workflows/ci.yml)

# Qmonus-PluginBuilder
Qmonus-PluginBuilderは、VSCodeやPyCharm等のエディタでQmonus-SDKのPlugin開発ができるpythonベースのフレームワークです。

## 機能
Qmonus-SDKのPlugin開発の際、以下のようなエディタの持つ開発支援機能をそのまま利用可能です。
- Autocomplete
- Static Type Checking
- Syntax Highlighting
- Refactoring
- など

コーディング後は、CLIコマンドによりQmonus-SDK用のPlugin（YAMLファイル）を出力できます。Plugin（YAMLファイル）からpython scriptの生成はできません。

## サポート対象の機能
`class`、`module`、`scenario`、`daemon`をサポートしています。

## インストール
`pip install`を実行してください。venvの利用を推奨します。
```
pip install -U git+https://github.com/qmonus/plugin-builder.git@1.3.0
```

## 利用方法
### 開発の流れ
以下のようになります。

1. `initコマンド`により`project`を作成します。qmonus_sdk_pluginsディレクトリが生成されます。[ディレクトリ構造](#ディレクトリ構造)を参考にしてください。
2. qmonus_sdk_plugins内にpython scriptを記述します。`initコマンド`により生成される雛形([classの雛形](src/qmonus_plugin_builder/init_files/qmonus_sdk_plugins/plugins/default/classes/default/User.py)、[moduleの雛形](src/qmonus_plugin_builder/init_files/qmonus_sdk_plugins/plugins/default/modules/default/constants.py)、[scenarioの雛形](src/qmonus_plugin_builder/init_files/qmonus_sdk_plugins/plugins/default/scenarios/default/CreateUser.py)、[daemonの雛形](src/qmonus_plugin_builder/init_files/qmonus_sdk_plugins/plugins/default/daemons/default/Log.py))を参考にしてください。`class`や`module`の追加・変更・削除を実施した場合は`updateコマンド`で`project`の更新処理を実施します（Static Type Checkingなどに必要な情報が生成されます）。
3. `dumpコマンド`を使いYAMLファイルを生成します。

### CLI
- 作成
  - `initコマンド`により、`project`を作成します。
    - qmonus_sdk_pluginsディレクトリが生成されます。
    - qmonus_sdk_pluginsはpythonモジュールです。
    - qmonus_sdk_plugins内には、`class`、`module`、`scenario`、`daemon`が生成されます。[ディレクトリ構造](#ディレクトリ構造)を参考にしてください。

```
format:
python -m qmonus_plugin_builder init {project_path}

example:
python -m qmonus_plugin_builder init .
```

- 更新
  - `class`または`module`を追加したり削除したりした場合は、`updateコマンド`を実行してください。
  - 更新により、Static Type Checkingなどに必要な情報が`libs`ディレクトリ配下に生成されます。

```
format:
python -m qmonus_plugin_builder update {project_path}

example:
python -m qmonus_plugin_builder update .
```

- YAMLファイル生成
  - `dumpコマンド`により、任意のディレクトリにYAMLファイルを出力します。
  - 内部的には`updateコマンド`の処理を実施してからYAMLファイルの生成が行われます。
  - 下記の例では、`../axis`にYAMLファイルを出力しています。

```
format:
python -m qmonus_plugin_builder dump {project_path} {YAML出力先のpath}

example:
python -m qmonus_plugin_builder dump . ../axis
```

### ディレクトリ構造
```
{project_path}/
+-- qmonus_sdk_plugins/
    +-- __init__.py
    +-- libs/                                 # updateコマンドにより自動生成されるディレクトリ
    +-- plugins/
        +-- __init__.py
        +-- {workspace_name_1}/               # workspace名
            +-- __init__.py
            +-- classes/                      # classを記述するディレクトリ
            |   +-- __init__.py
            |   +-- {category_name_1}/        # カテゴリ名
            |       +-- __init__.py
            |       +-- {class_name_1}.py     # classを記述するファイル
            |       +-- {class_name_2}.py
            |       .
            |       +-- {class_name_n}.py
            +-- modules/                      # moduleを記述するディレクトリ
            |   +-- __init__.py
            |   +-- {category_name_1}/        # カテゴリ名
            |       +-- __init__.py
            |       +-- {module_name_1}.py    # moduleを記述するファイル
            |       +-- {module_name_2}.py
            |       .
            |       +-- {module_name_n}.py
            +-- scenarios/                    # scenarioを記述するディレクトリ
            |   +-- __init__.py
            |   +-- {category_name_1}/        # カテゴリ名
            |       +-- __init__.py
            |       +-- {scenario_name_1}.py  # scenarioを記述するファイル
            |       +-- {scenario_name_2}.py
            |       .
            |       +-- {scenario_name_n}.py
            +-- daemons/                      # daemonを記述するディレクトリ
                +-- __init__.py
                +-- {category_name_1}/        # カテゴリ名
                    +-- __init__.py
                    +-- {daemon_name_1}.py    # daemonを記述するファイル
                    +-- {daemon_name_2}.py
                    .
                    +-- {daemon_name_n}.py
```
