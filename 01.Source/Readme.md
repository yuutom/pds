# OpenAPI

## 概要
PDSの公開APIを管理する<br>
公開APIには「トークン発行」、「個人情報参照」、「個人情報検索」、「個人情報登録」、「個人情報更新」、「個人情報削除」の6つのAPIが存在する。

<br>
<hr>
<br>

## 初回起動方法
**詳しい環境構築方法は、「環境構築.xlsx」の「FastAPI関連」シートを確認してください**
### ①Pythonモジュールを導入してください
ターミナルで下記のコマンドを実行
pip install --no-cache-dir -r ./requirements.txt
### ②FastAPIを起動
ターミナルで下記のコマンドを実行
uvicorn app:app --reload

<br>
<hr>
<br>

## フォルダ構成
下記のようなフォルダ構成で作成している。

<dl>
    <dt><h3>.vscode</h3></dt>
    <dd>VSCodeのデバッグ設定ファイルを格納している</dd>
    <dt><h3>OpenAPI</h3></dt>
    <dd>公開APIの処理が格納されている <b>(プログラムはこのフォルダに配置されている)</b> </dd>
    <dt><h3>OpenAPI/const</h3></dt>
    <dd>定数を記載する。</dd>
    <dt><h3>OpenAPI/models</h3></dt>
    <dd>ビジネスロジックを記載する。(MVCモデルのM)</dd>
    <dt><h3>OpenAPI/routers</h3></dt>
    <dd>APIのルートをコントロールする。(MVCモデルのC)</dd>
    <dt><h3>OpenAPI/util</h3></dt>
    <dd>ユーティリティクラスを格納する</dd>
    <dt><h3>OpenAPI/app.py</h3></dt>
    <dd>FastAPIの全体設定を記載するファイル。</dd>
    <dt><h3>OpenAPI/log_config.json</h3></dt>
    <dd>ログ出力の設定ファイル。</dd>
    <dt><h3>Readme.md</h3></dt>
    <dd>
        このプログラムの説明ファイル。今見えてるものはここに記載されています。</br>
        VSCode上で確認したい場合は、「表示」→「コマンドパレット」を選択して「Markdown: プレビューを横に表示」をしてください。
    </dd>
    <dt><h3>requirements.txt</h3></dt>
    <dd>Pypiモジュールの管理ファイル(pipコマンドを使ったら更新してください)</dd>
</dl>
