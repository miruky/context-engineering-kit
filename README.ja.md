# コンテキストエンジニアリングの導入テンプレート

AIへ渡す仕様書・コード・ログを選び、必要な範囲の情報をひとつにまとめます。元のファイルの変更を検出し、作成済みの情報を更新する必要があるか確認します。

[英語版](README.en.md) · [操作手順](docs/USAGE.md) · [設計と制約](docs/ARCHITECTURE.md)

## クローン後に試す

必要なものはGitと **Python 3.10以上** です。Pythonはこのツールを動かすために使い、対象アプリの開発言語は限定していません。付属の利用例には、追加パッケージやAPIキーは不要です。

クローンしたディレクトリで実行してください。

```sh
# 実行環境と付属の利用例を確認します
python3 kit.py doctor
python3 kit.py demo
```

Windowsでは `python3` を `py -3` へ置き換えてください。`dev.cmd` やPowerShellの `./dev.ps1` も使えます。macOS・Linuxでは `./dev` が短い呼び出し方です。

`demo` は一時的な作業場所で動きます。クローンしたテンプレートの設定や成果物を、確認済みの状態へ変更しません。

## 情報を作成する

`.agentkit/context.json` に対象ファイル、優先度、容量の上限を設定します。

```sh
# 設定した資料から、今回の依頼に使う情報を作成します
python3 kit.py pack --task "仕様に沿って成果物を更新する"
```

出力されたMarkdownを、使いたいAIへ渡してください。`verify` では元ファイルの追加・削除・変更を確認できます。コマンドの詳しい使い方は [操作手順](docs/USAGE.md) にあります。

容量の上限にはUTF-8のバイト数を指定します。指示、参考資料、外部の情報には出所の区分を付けます。外部の文章に含まれる命令が自動で無害化されるわけではないため、渡す内容は事前に確認してください。

## 自分のプロジェクトへ導入する

新しく始める場合は、空の作業場所を作成できます。

```sh
# テンプレートと実行ツールを新しい作業場所へコピーします
python3 kit.py new ../my-project
```

既存のプロジェクトへ追加する場合は、追加予定のファイルを確認してから適用します。

```sh
# 追加内容を確認してから適用します
python3 kit.py install --target ../existing-project
python3 kit.py install --target ../existing-project --apply
```

既存のAGENTS.md、CLAUDE.md、設定、フックは上書きしません。`.agentkit/context.example.json` のパスやコマンドを実際のプロジェクトへ合わせ、`.agentkit/context.json` として保存してください。導入先のディレクトリでは `python3 .agentkit/tools/context/kit.py --root . inspect` で設定を確認できます。

## 設計上の範囲

このテンプレートは手元で使う開発用ツールです。ローカルの設定や記録は、利用者自身が変更できます。実行権限を制限する場合は、認証情報や実行環境側でも制御してください。詳しい対応範囲は [設計と制約](docs/ARCHITECTURE.md) に記載しています。

ツール自体を変更したときの検査は `python3 kit.py check` で実行できます。ライセンスは [MIT](LICENSE) です。第三者のコードの出典は [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。
