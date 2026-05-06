# 要件定義書

## はじめに

本ドキュメントは、商品情報管理Webアプリケーションの要件を定義する。本アプリケーションは、Amazon Cognitoによるユーザー認証を経て、商品情報（商品ID、商品名称、価格、商品概要、商品画像）のCRUD操作を提供するWebアプリケーションである。バックエンドはAWS サーバーレスアーキテクチャ（API Gateway、Lambda、DynamoDB、S3）で構成し、フロントエンドはNext.js（TypeScript）で構築する。

## 用語集

- **System**: 商品情報管理Webアプリケーション全体を指す
- **Frontend**: Next.js（TypeScript）で構築されたフロントエンドアプリケーション
- **Backend**: API Gateway、Lambda関数で構成されるバックエンドサービス
- **Auth_Service**: Amazon Cognitoユーザープールによる認証サービス
- **Product_API**: 商品情報のCRUD操作を提供するREST API
- **Product_Store**: Amazon DynamoDBの商品情報テーブル
- **Image_Store**: Amazon S3バケットによる商品画像ストレージ
- **Image_CDN**: Amazon CloudFrontディストリビューションによる画像配信サービス
- **User**: Cognitoユーザープールに登録されたアプリケーション利用者
- **Product**: 商品ID、商品名称、価格、商品概要、商品画像で構成される商品情報エンティティ
- **SAM_Template**: AWS SAM（Serverless Application Model）テンプレートファイルによるインフラストラクチャ定義
- **SAM_CLI**: AWS SAM CLIツールによるビルド・デプロイ操作

## 要件

### 要件 1: ユーザー認証

**ユーザーストーリー:** ユーザーとして、Cognitoユーザープールの認証情報でサインインしたい。これにより、認証されたユーザーのみが商品情報にアクセスできるようになる。

#### 受け入れ基準

1. WHEN User が有効な認証情報（メールアドレスとパスワード）を入力した場合、THE Auth_Service SHALL User を認証し、アクセストークンを発行する
2. WHEN User が無効な認証情報を入力した場合、THE Auth_Service SHALL 認証エラーメッセージを表示する
3. WHILE User が認証されていない状態では、THE Frontend SHALL サインイン画面のみを表示する
4. WHEN User がサインアウト操作を行った場合、THE Auth_Service SHALL セッションを無効化し、Frontend はサインイン画面にリダイレクトする
5. THE Auth_Service SHALL ユーザーの自己サインアップを禁止し、管理者のみがユーザーを作成可能とする

### 要件 2: 商品一覧表示

**ユーザーストーリー:** ユーザーとして、サインイン後に商品情報の一覧を確認したい。これにより、登録済みの商品を把握できるようになる。

#### 受け入れ基準

1. WHEN User がサインインに成功した場合、THE Frontend SHALL 商品情報の一覧画面を表示する
2. THE Product_API SHALL Product_Store から全商品情報を取得し、一覧データとして返却する
3. THE Frontend SHALL 各商品の商品ID、商品名称、価格、商品概要、商品画像を一覧に表示する
4. WHEN Product_Store に商品情報が存在しない場合、THE Frontend SHALL 「商品情報がありません」というメッセージを表示する
5. IF Product_API からのデータ取得に失敗した場合、THEN THE Frontend SHALL エラーメッセージを表示し、再試行ボタンを提供する

### 要件 3: 商品情報追加

**ユーザーストーリー:** ユーザーとして、新しい商品情報を追加したい。これにより、取り扱い商品を管理できるようになる。

#### 受け入れ基準

1. WHEN User が商品追加操作を行った場合、THE Frontend SHALL 商品情報入力フォームを表示する
2. THE Frontend SHALL 商品名称、価格、商品概要、商品画像の入力フィールドを提供する
3. WHEN User が有効な商品情報を入力し送信した場合、THE Product_API SHALL 一意の商品IDを生成し、商品情報を Product_Store に保存する
4. WHEN User が商品画像をアップロードした場合、THE Product_API SHALL 画像ファイルを Image_Store に保存し、画像の参照URLを Product_Store に記録する
5. IF 必須項目（商品名称、価格）が未入力の場合、THEN THE Frontend SHALL バリデーションエラーメッセージを表示し、送信を阻止する
6. WHEN 商品情報の保存が成功した場合、THE Frontend SHALL 成功メッセージを表示し、商品一覧画面に遷移する
7. IF 商品情報の保存に失敗した場合、THEN THE Frontend SHALL エラーメッセージを表示し、入力内容を保持する

### 要件 4: 商品情報編集

**ユーザーストーリー:** ユーザーとして、既存の商品情報を編集したい。これにより、商品情報を最新の状態に保てるようになる。

#### 受け入れ基準

1. WHEN User が一覧から商品の編集操作を行った場合、THE Frontend SHALL 該当商品の情報が入力済みの編集フォームを表示する
2. THE Frontend SHALL 商品名称、価格、商品概要、商品画像の編集を許可する
3. WHEN User が編集内容を送信した場合、THE Product_API SHALL Product_Store の該当商品情報を更新する
4. WHEN User が商品画像を変更した場合、THE Product_API SHALL 新しい画像を Image_Store に保存し、古い画像を Image_Store から削除し、Product_Store の画像参照URLを更新する
5. IF 必須項目（商品名称、価格）が未入力の場合、THEN THE Frontend SHALL バリデーションエラーメッセージを表示し、送信を阻止する
6. WHEN 商品情報の更新が成功した場合、THE Frontend SHALL 成功メッセージを表示し、商品一覧画面に遷移する
7. IF 商品情報の更新に失敗した場合、THEN THE Frontend SHALL エラーメッセージを表示し、編集内容を保持する

### 要件 5: 商品情報削除

**ユーザーストーリー:** ユーザーとして、不要な商品情報を削除したい。これにより、商品リストを整理できるようになる。

#### 受け入れ基準

1. WHEN User が一覧から商品の削除操作を行った場合、THE Frontend SHALL 削除確認ダイアログを表示する
2. WHEN User が削除を確認した場合、THE Product_API SHALL Product_Store から該当商品情報を削除する
3. WHEN 削除対象の商品に画像が関連付けられている場合、THE Product_API SHALL Image_Store から該当画像も削除する
4. WHEN 商品情報の削除が成功した場合、THE Frontend SHALL 成功メッセージを表示し、商品一覧を更新する
5. IF 商品情報の削除に失敗した場合、THEN THE Frontend SHALL エラーメッセージを表示する
6. WHEN User が削除確認ダイアログでキャンセルを選択した場合、THE Frontend SHALL 削除処理を中止し、一覧画面の状態を維持する

### 要件 6: API認可

**ユーザーストーリー:** システム管理者として、認証済みユーザーのみがAPIにアクセスできるようにしたい。これにより、不正アクセスからデータを保護できるようになる。

#### 受け入れ基準

1. THE Product_API SHALL すべてのエンドポイントでCognito認証トークンの検証を要求する
2. WHEN 有効な認証トークンを含むリクエストを受信した場合、THE Product_API SHALL リクエストを処理する
3. IF 認証トークンが無効または期限切れの場合、THEN THE Product_API SHALL 401 Unauthorizedレスポンスを返却する
4. IF 認証トークンが存在しない場合、THEN THE Product_API SHALL 401 Unauthorizedレスポンスを返却する

### 要件 7: 商品画像管理

**ユーザーストーリー:** ユーザーとして、商品に画像を関連付けて管理したい。これにより、商品を視覚的に識別できるようになる。

#### 受け入れ基準

1. THE Image_Store SHALL 商品画像ファイルを安全に保存し、パブリックアクセスを禁止する
2. WHEN User が画像をアップロードする場合、THE Product_API SHALL 画像ファイル形式（JPEG、PNG、WebP）を検証する
3. IF アップロードされたファイルが許可されていない形式の場合、THEN THE Product_API SHALL エラーメッセージを返却し、アップロードを拒否する
4. THE System SHALL CloudFrontディストリビューション経由で商品画像をFrontendに提供する
5. THE System SHALL CloudFrontにオリジンアクセスコントロール（OAC）を設定し、S3バケットへの直接アクセスを禁止する
6. THE Image_Store SHALL CloudFrontディストリビューションからのアクセスのみを許可するバケットポリシーを設定する
7. WHEN 商品画像が登録されていない商品を表示する場合、THE Frontend SHALL デフォルトのプレースホルダー画像を表示する

### 要件 8: プロジェクト構造

**ユーザーストーリー:** 開発者として、フロントエンドとバックエンドのコードを分離して管理したい。これにより、独立した開発とデプロイが可能になる。

#### 受け入れ基準

1. THE System SHALL フロントエンドコードとバックエンドコードを別々のディレクトリで管理する
2. THE Frontend SHALL Next.js（TypeScript）のApp Routerを使用してシンプルな構造で構築する
3. THE Backend SHALL AWS Lambda関数とAPI Gateway設定を含む
4. THE System SHALL フロントエンドディレクトリとバックエンドディレクトリをプロジェクトルートに配置する

### 要件 9: バックエンドデプロイ

**ユーザーストーリー:** 開発者として、AWS SAMを使用してバックエンドをデプロイしたい。これにより、インフラストラクチャをコードとして管理し、再現可能なデプロイが可能になる。

#### 受け入れ基準

1. THE Backend SHALL AWS SAMテンプレート（template.yaml）でAPI Gateway、Lambda関数、DynamoDB、S3の全リソースを定義する
2. THE Backend SHALL SAM_CLI の `sam build` コマンドでビルド可能な構成とする
3. THE Backend SHALL SAM_CLI の `sam deploy` コマンドでAWS環境にデプロイ可能な構成とする
4. THE Backend SHALL すべてのLambda関数のランタイムにPython 3.13を使用する
5. THE SAM_Template SHALL Cognito User Pool、API Gateway Authorizer、DynamoDBテーブル、S3バケット、CloudFrontディストリビューションのリソース定義を含む
6. THE SAM_Template SHALL 環境ごとのパラメータ（ステージ名等）を外部から指定可能とする
7. IF SAM_CLI によるビルドが失敗した場合、THEN THE Backend SHALL エラーの原因を特定可能なログを出力する
