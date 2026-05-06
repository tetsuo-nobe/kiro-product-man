# 実装計画: 商品情報管理Webアプリケーション

## 概要

本実装計画は、AWS サーバーレスアーキテクチャを基盤とした商品情報管理Webアプリケーションの実装タスクを定義する。バックエンドのインフラ・基盤から始め、ビジネスロジック、最後にフロントエンドの順序で実装を進める。

- バックエンド: Python 3.13 (AWS Lambda + SAM)
- フロントエンド: TypeScript (Next.js App Router)
- テスト: pytest + Hypothesis (バックエンド), Jest + React Testing Library (フロントエンド)

## タスク

- [x] 1. プロジェクト構造とSAMテンプレートの作成
  - [x] 1.1 プロジェクトディレクトリ構造を作成する
    - `backend/` と `frontend/` のディレクトリ構造を設計書に従って作成
    - `backend/src/handlers/`, `backend/src/models/`, `backend/src/utils/` を作成
    - `backend/tests/unit/`, `backend/tests/property/`, `backend/tests/integration/` を作成
    - 各ディレクトリに `__init__.py` を配置
    - _Requirements: 8.1, 8.3, 8.4_

  - [x] 1.2 SAMテンプレート（template.yaml）を作成する
    - Parameters セクション（StageName: dev/staging/prod）
    - Globals セクション（Runtime: python3.13, MemorySize: 256, Timeout: 30, 環境変数）
    - Cognito User Pool（`AdminCreateUserConfig: AllowAdminCreateUserOnly: true` で自己サインアップ無効化）
    - Cognito User Pool Client（USER_PASSWORD_AUTH, REFRESH_TOKEN_AUTH）
    - API Gateway REST API（Cognito Authorizer付き、CORS設定）
    - Lambda関数4つ（ListProducts, CreateProduct, UpdateProduct, DeleteProduct）とIAMポリシー
    - DynamoDB Products テーブル（PAY_PER_REQUEST, productId: HASH）
    - S3バケット（`PublicAccessBlockConfiguration` で全パブリックアクセス禁止、CORS設定、ライフサイクルルール）
    - S3バケットポリシー（CloudFrontサービスプリンシパルからのGetObjectのみ許可、SourceArn条件付き）
    - CloudFront Origin Access Control（OAC: SigningBehavior: always, SigningProtocol: sigv4）
    - CloudFront Distribution（OAC設定、CachingOptimized、redirect-to-https）
    - Outputs セクション（ApiUrl, UserPoolId, UserPoolClientId, ImageBucketName, CloudFrontDomain, CloudFrontDistributionId）
    - _Requirements: 9.1, 9.5, 9.6, 1.5, 6.1, 7.1, 7.4, 7.5, 7.6_

  - [x] 1.3 SAMデプロイ設定（samconfig.toml）とPython依存パッケージ（requirements.txt）を作成する
    - samconfig.toml にデフォルトのデプロイパラメータを設定
    - requirements.txt に boto3 等の依存パッケージを記載
    - テスト用 requirements-dev.txt に pytest, hypothesis, moto 等を記載
    - _Requirements: 9.2, 9.3, 9.4_

- [x] 2. バックエンド共通モジュールの実装
  - [x] 2.1 商品モデル（models/product.py）を実装する
    - Product dataclass の定義（product_id, product_name, price, description, image_key, created_at, updated_at）
    - `to_dict()` メソッド: DynamoDB保存用辞書への変換（Optional項目はNone時に除外）
    - `from_dict()` クラスメソッド: DynamoDBアイテムからのインスタンス生成
    - _Requirements: 3.3, 4.3_

  - [ ]* 2.2 プロパティテスト: 商品データシリアライゼーションのラウンドトリップ
    - **Property 1: 商品データシリアライゼーションのラウンドトリップ**
    - Hypothesisを使用して任意の有効なProductオブジェクトに対し `to_dict()` → `from_dict()` の往復変換が等価であることを検証
    - **Validates: Requirements 3.3, 4.3**

  - [x] 2.3 バリデーションモジュール（utils/validation.py）を実装する
    - `validate_product_data(data)`: 商品名称（必須、1〜200文字）、価格（必須、0以上の整数）、商品概要（任意、最大2000文字）のバリデーション
    - `ValidationError` カスタム例外クラスの定義
    - `NotFoundError` カスタム例外クラスの定義
    - _Requirements: 3.5, 4.5_

  - [ ]* 2.4 プロパティテスト: 商品バリデーション - 必須項目欠如の拒否
    - **Property 2: 商品バリデーション - 必須項目欠如の拒否**
    - Hypothesisを使用して商品名称が空文字列/空白のみ、または価格が未指定/負数の場合にバリデーションエラーが発生することを検証
    - **Validates: Requirements 3.5, 4.5**

  - [x] 2.5 画像処理ユーティリティ（utils/image.py）を実装する
    - `validate_image_format(content_type, file_content)`: JPEG/PNG/WebPのマジックバイトによる形式検証
    - `generate_image_key(product_id, extension)`: S3オブジェクトキーの生成（`products/{productId}/{uuid}.{ext}` 形式）
    - `validate_image_size(file_content)`: 最大ファイルサイズ（5MB）の検証
    - _Requirements: 7.2, 7.3_

  - [ ]* 2.6 プロパティテスト: 画像形式バリデーション
    - **Property 3: 画像形式バリデーション**
    - Hypothesisを使用してJPEG/PNG/WebP形式のみバリデーション成功し、それ以外は拒否されることを検証
    - **Validates: Requirements 7.2, 7.3**

  - [x] 2.7 レスポンスヘルパー（utils/response.py）を実装する
    - `success_response(status_code, body)`: 成功レスポンス生成（CORSヘッダー付与）
    - `error_response(status_code, error_type, message)`: エラーレスポンス生成
    - `handle_exceptions` デコレータ: Lambda関数の共通例外ハンドリング（ValidationError→400, NotFoundError→404, Exception→500）
    - _Requirements: 6.3, 6.4_

- [x] 3. チェックポイント - 共通モジュールの確認
  - すべてのテストが通ることを確認し、不明点があればユーザーに質問する。

- [x] 4. Lambda関数ハンドラの実装
  - [x] 4.1 商品一覧取得（handlers/list_products.py）を実装する
    - DynamoDB Scanで全商品取得
    - 各商品の imageKey から CloudFront URL を生成（`https://{CLOUDFRONT_DOMAIN}/{imageKey}`）
    - imageKey が無い商品は imageUrl を null として返却
    - レスポンスに productId, productName, price, description, imageUrl, createdAt, updatedAt を含める
    - _Requirements: 2.2, 2.3, 7.4_

  - [ ]* 4.2 プロパティテスト: 商品一覧レスポンスの完全性
    - **Property 5: 商品一覧レスポンスの完全性**
    - Hypothesisを使用して任意の有効なProductオブジェクトのAPIレスポンス変換結果に必須フィールド（productId, productName, price, createdAt, updatedAt）がすべて含まれることを検証
    - **Validates: Requirements 2.3**

  - [x] 4.3 商品追加（handlers/create_product.py）を実装する
    - multipart/form-data のパース（base64デコード対応）
    - バリデーション実行（validate_product_data）
    - UUID v4 で商品ID生成（`prod-{uuid}` 形式）
    - 画像ファイルがある場合、形式・サイズ検証後にS3にアップロード
    - DynamoDBに商品情報を保存（createdAt, updatedAt を ISO 8601 形式で設定）
    - CloudFront URLを含むレスポンス返却（201 Created）
    - _Requirements: 3.3, 3.4, 3.5, 3.6, 7.2, 7.3_

  - [ ]* 4.4 プロパティテスト: 商品ID一意性
    - **Property 4: 商品ID一意性**
    - Hypothesisを使用して複数回の商品ID生成で衝突が発生しないことを検証
    - **Validates: Requirements 3.3**

  - [x] 4.5 商品更新（handlers/update_product.py）を実装する
    - パスパラメータから商品ID取得
    - DynamoDBから既存商品情報取得（存在しない場合 NotFoundError → 404）
    - multipart/form-data のパース・バリデーション
    - 画像変更がある場合、新画像をS3にアップロード後、旧画像をS3から削除
    - DynamoDBの商品情報を更新（updatedAt を更新）
    - CloudFront URLを含むレスポンス返却（200 OK）
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 4.6 商品削除（handlers/delete_product.py）を実装する
    - パスパラメータから商品ID取得
    - DynamoDBから既存商品情報取得（画像キー確認）
    - 画像が存在する場合、S3から削除
    - DynamoDBから商品情報を削除
    - 成功レスポンス返却（200 OK）
    - _Requirements: 5.2, 5.3_

  - [ ]* 4.7 単体テスト: Lambda関数ハンドラのテスト
    - motoを使用してDynamoDB、S3をモック
    - 各ハンドラの正常系テスト（一覧取得、追加、更新、削除）
    - 各ハンドラの異常系テスト（バリデーションエラー、リソース未検出、画像形式エラー）
    - _Requirements: 2.2, 3.3, 3.5, 4.3, 4.5, 5.2, 7.2, 7.3_

- [x] 5. チェックポイント - バックエンド実装の確認
  - すべてのテストが通ることを確認し、`sam validate` と `sam build` が成功することを確認する。不明点があればユーザーに質問する。

- [x] 6. フロントエンドプロジェクトのセットアップ
  - [x] 6.1 Next.jsプロジェクトを初期化する
    - `frontend/` ディレクトリにNext.js（TypeScript, App Router）プロジェクトを作成
    - package.json に必要な依存パッケージを追加（amazon-cognito-identity-js 等のCognito SDK）
    - tsconfig.json の設定（strict mode, paths alias）
    - next.config.js の設定（images.remotePatterns でCloudFrontドメインを許可）
    - 環境変数ファイル（.env.local.example）の作成
    - _Requirements: 8.2_

  - [x] 6.2 型定義（lib/types.ts）を作成する
    - Product インターフェース（productId, productName, price, description?, imageUrl?, createdAt, updatedAt）
    - ProductFormData インターフェース（productName, price, description?, image?）
    - AuthResult インターフェース（idToken, accessToken, refreshToken）
    - ApiError インターフェース（error, message）
    - _Requirements: 2.3, 3.2_

  - [x] 6.3 認証ユーティリティ（lib/auth.ts）を実装する
    - `signIn(email, password)`: Cognito USER_PASSWORD_AUTH フローでサインイン（InitiateAuth API）
    - `signOut()`: GlobalSignOut + sessionStorageからトークン削除 + サインイン画面リダイレクト
    - `getIdToken()`: sessionStorageからIDトークンの取得
    - `isAuthenticated()`: トークン存在による認証状態の確認
    - トークンのsessionStorage保存（idToken, accessToken, refreshToken）
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 6.4 APIクライアント（lib/api.ts）を実装する
    - `listProducts()`: GET /products → Product[]
    - `createProduct(data: ProductFormData)`: POST /products (multipart/form-data) → Product
    - `updateProduct(productId, data: ProductFormData)`: PUT /products/{productId} (multipart/form-data) → Product
    - `deleteProduct(productId)`: DELETE /products/{productId} → void
    - 認証トークン（IDトークン）の自動付与（Authorization: Bearer ヘッダー）
    - 401レスポンス時のトークン削除とサインイン画面リダイレクト
    - NetworkError, ApiRequestError カスタムエラークラスの定義
    - _Requirements: 6.2, 6.3, 6.4_

- [x] 7. フロントエンドページ・コンポーネントの実装
  - [x] 7.1 ルートレイアウト（app/layout.tsx）と共通レイアウトコンポーネント（components/Layout.tsx）を実装する
    - ルートレイアウト: html/body タグ、メタデータ、グローバルスタイル読み込み
    - Layout コンポーネント: ヘッダー（アプリ名「商品管理」、サインアウトボタン）、メインコンテンツエリア
    - グローバルスタイル（styles/globals.css）
    - _Requirements: 1.4_

  - [x] 7.2 サインイン画面（app/login/page.tsx）を実装する
    - 'use client' ディレクティブ（Client Component）
    - メールアドレス・パスワード入力フォーム
    - サインインボタン（ローディング状態対応）
    - 認証エラーメッセージ表示
    - 認証成功時の商品一覧画面（/）へのリダイレクト（router.push）
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 7.3 商品一覧画面（app/page.tsx）と商品一覧コンポーネント（components/ProductList.tsx）を実装する
    - 'use client' ディレクティブ（Client Component）
    - 未認証時のサインイン画面リダイレクト
    - 商品カード一覧表示（商品名称、価格、商品概要、商品画像）
    - 商品画像はCloudFront URLで表示（next/image の remotePatterns 使用）
    - 画像未登録商品にはプレースホルダー画像（/placeholder.png）を表示
    - 各商品に編集・削除ボタン
    - 商品追加ボタン（/products/new へ遷移）
    - 商品が0件の場合「商品情報がありません」メッセージ表示
    - データ取得失敗時のエラーメッセージ・再試行ボタン
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 7.4, 7.7_

  - [x] 7.4 商品入力フォーム（components/ProductForm.tsx）を実装する
    - 'use client' ディレクティブ（Client Component）
    - 商品名称（テキスト入力、必須）、価格（数値入力、必須）、商品概要（テキストエリア、任意）、商品画像（ファイル入力、任意）
    - クライアントサイドバリデーション（商品名称: 必須・1〜200文字、価格: 必須・0以上の整数）
    - 画像プレビュー表示（FileReader API使用）
    - 追加・編集共用（initialData props の有無で切り替え）
    - バリデーションエラーメッセージ表示（各フィールド横）
    - 送信ボタン（ローディング状態対応）
    - _Requirements: 3.2, 3.5, 4.2, 4.5_

  - [x] 7.5 商品追加画面（app/products/new/page.tsx）を実装する
    - 'use client' ディレクティブ（Client Component）
    - 未認証時のサインイン画面リダイレクト
    - ProductFormを使用した新規商品追加
    - 保存成功時の成功メッセージ表示と一覧画面（/）遷移（router.push）
    - 保存失敗時のエラーメッセージ表示と入力内容保持
    - _Requirements: 3.1, 3.6, 3.7_

  - [x] 7.6 商品編集画面（app/products/[id]/edit/page.tsx）を実装する
    - 'use client' ディレクティブ（Client Component）
    - 未認証時のサインイン画面リダイレクト
    - パスパラメータ（params.id）から商品IDを取得
    - 既存商品情報をAPIから取得し、ProductFormに初期値として設定
    - 更新成功時の成功メッセージ表示と一覧画面（/）遷移
    - 更新失敗時のエラーメッセージ表示と編集内容保持
    - _Requirements: 4.1, 4.6, 4.7_

  - [x] 7.7 削除確認ダイアログ（components/DeleteDialog.tsx）を実装する
    - 'use client' ディレクティブ（Client Component）
    - 削除確認メッセージ表示（「この商品を削除しますか？」）
    - 確認ボタン・キャンセルボタン
    - 削除成功時の成功メッセージ表示と一覧更新（コールバック経由）
    - 削除失敗時のエラーメッセージ表示
    - キャンセル時のダイアログ閉じ（一覧画面状態維持）
    - _Requirements: 5.1, 5.4, 5.5, 5.6_

  - [ ]* 7.8 フロントエンド単体テストを作成する
    - Jest + React Testing Library のセットアップ
    - ProductList コンポーネントのテスト（一覧表示、空状態、エラー状態、プレースホルダー画像）
    - ProductForm コンポーネントのテスト（バリデーション、送信、画像プレビュー）
    - DeleteDialog コンポーネントのテスト（確認、キャンセル、エラー表示）
    - 認証ユーティリティのテスト（signIn成功/失敗、signOut、トークン管理）
    - _Requirements: 2.3, 2.4, 3.5, 5.1, 5.6_

- [x] 8. チェックポイント - 全体統合確認
  - すべてのテストが通ることを確認し、不明点があればユーザーに質問する。

## 備考

- `*` マーク付きのタスクはオプションであり、MVP実装時にはスキップ可能
- 各タスクは特定の要件にトレースバック可能
- チェックポイントでは段階的な検証を実施
- プロパティテストは正当性プロパティの機械的検証を目的とする（Hypothesis使用）
- 単体テストは具体的な例とエッジケースの検証を目的とする
- フロントエンドはNext.js App Routerを使用し、Client Componentには 'use client' ディレクティブを付与する
- 商品画像はCloudFront OAC経由で配信し、S3への直接アクセスは禁止する
- Cognitoユーザープールは自己サインアップを無効化し、管理者のみがユーザーを作成可能とする
