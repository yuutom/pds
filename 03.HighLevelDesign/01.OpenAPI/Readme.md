# 公開API 基本設計資料

## 概要
PDSの公開APIの基本設計資料<br>
APIの基本設計資料はOpenApiのYAML形式で記載する。<br>
書き方は下記URLを参照して作成しました。
<ul>
    <li>OpenAPI (Swagger) 超入門</li>
        基本的な記載方法はここを参照<br>
        <p>https://qiita.com/teinen_qiita/items/e440ca7b1b52ec918f1b</p>
    <li>OpenAPIのYAMLをVSCodeで分割管理する</li>
        フォルダ構成はここを参照<br>
        <p>https://qiita.com/tMinamiii/items/5b1a921e82b4c7979cd1<p>
    <li>OpenApiのYAML分割管理と構成案</li>
        分割ファイルの記載方法はここを参照<br>
        <p>https://qiita.com/KUMAN/items/543b147651dc32065191</p>
</ul>

<br>
<hr>
<br>

## フォルダ構成
下記のようなフォルダ構成で作成している。

<dl>
    <dt><h3>components</h3></dt>
    <dd>
        OpenApiのcomponents属性を記載する。<br>
        API間で共通利用されるリクエスト・レスポンスパラメータを記載する。
    </dd>
    <dt><h3>components/header</h3></dt>
    <dd>ヘッダに付与されるパラメータを記載する</dd>
    <dt><h3>components/parameters</h3></dt>
    <dd>リクエスト・レスポンスのボディに付与されたパラメータを記載する</dd>
    <dt><h3>paths</h3></dt>
    <dd>
        OpenApiのpaths属性を記載する。<br>
        API毎の設計情報を記載する。<br>
        pathsフォルダの中のフォルダ分割単位は「openapi.yaml」のグループ属性の単位で分割する。
    </dd>
    <dt><h3>openapi.yaml</h3></dt>
    <dd>
        基本設計書の元になっているファイル。
    </dd>
    <dt><h3>openapi.html</h3></dt>
    <dd>YAMLファイルから作成したHTML</dd>
    <dt><h3>Readme.md</h3></dt>
    <dd>
        このプログラムの説明ファイル。今見えてるものはここに記載されています。</br>
        VSCode上で確認したい場合は、「表示」→「コマンドパレット」を選択して「Markdown: プレビューを横に表示」をしてください。
    </dd>
</dl>
