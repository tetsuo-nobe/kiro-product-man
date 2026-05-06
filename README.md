# 商品情報管理アプリケーション

* このアプリケーションは Kiro の仕様駆動開発モードで構築しました。
* 最初のプロンプトは下記で、まずは requirements.md を生成させ、その後 設計、実装フェーズに進みました。

    ```
    商品情報を管理するWebアプリケーションを構築します。
    バックエンドにはAWSのAmazon API Gateway の REST API、Lambda 関数、DynamoDB、Amazon S3、Amazon Cognito を使用します。
    Lambda 関数のランタイムは Python 3.13 です。
    API Gateway では CORS の設定を行って下さい。もちろん OPTION メソッドは対象外です。
    バックエンドのデプロイは AWS SAM を使用します。
    フロントエンドにはNext.jsを使用します。
    Next.jsは、TypeScriptで App Router を使用し、できるだけシンプルな構造にして下さい。
    Cognitoユーザープールで管理するユーザーでサインインした後、商品情報の一覧が表示されます。
    一覧から商品情報の編集、削除、追加が可能です。
    商品情報は、商品ID、商品名称、価格、商品概要、商品画像で構成されます。
    商品画像はS3バケットで管理しますが、それ以外はDynamoDB で管理します。
    フロントエンドとバックエンドはフォルダを分けて管理します。
    ```

---

## アプリケーションの概要

商品の登録・一覧表示・編集・削除（CRUD）を行うフルスタック Web アプリケーションです。  
AWS サーバーレスアーキテクチャで構築されており、フロントエンドは Next.js、バックエンドは AWS SAM（Lambda + API Gateway + DynamoDB）で動作します。

## アーキテクチャ概要

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Next.js    │────▶│  API Gateway     │────▶│  Lambda     │
│  (Frontend) │     │  + Cognito Auth  │     │  (Python)   │
└─────────────┘     └──────────────────┘     └──────┬──────┘
                                                     │
                                          ┌──────────┼──────────┐
                                          ▼          ▼          ▼
                                    ┌──────────┐ ┌───────┐ ┌───────────┐
                                    │ DynamoDB │ │  S3   │ │CloudFront │
                                    └──────────┘ └───────┘ └───────────┘
```

### 使用サービス

| レイヤー | 技術 |
|---------|------|
| フロントエンド | Next.js 14 / React 18 / TypeScript |
| 認証 | Amazon Cognito（USER_PASSWORD_AUTH フロー） |
| API | Amazon API Gateway（REST API + Cognito Authorizer） |
| バックエンド | AWS Lambda（Python 3.13） |
| データベース | Amazon DynamoDB（オンデマンドキャパシティ） |
| 画像ストレージ | Amazon S3（パブリックアクセス禁止） |
| CDN | Amazon CloudFront（OAC 経由で S3 配信） |
| IaC | AWS SAM |

## 機能一覧

- **ユーザー認証**: Cognito によるメールアドレス + パスワード認証（自己サインアップ無効）
- **商品一覧表示**: 登録済み商品の一覧を表示
- **商品追加**: 商品名称・価格・商品概要・商品画像を登録
- **商品編集**: 既存商品情報の更新（画像差し替え対応）
- **商品削除**: 商品情報と関連画像の削除
- **画像管理**: JPEG / PNG / WebP 対応、最大 5MB、マジックバイト検証

## プロジェクト構成

```
.
├── backend/                    # バックエンド（AWS SAM）
│   ├── src/
│   │   ├── handlers/           # Lambda 関数ハンドラー
│   │   │   ├── create_product.py   # 商品追加
│   │   │   ├── list_products.py    # 商品一覧取得
│   │   │   ├── update_product.py   # 商品更新
│   │   │   └── delete_product.py   # 商品削除
│   │   ├── models/
│   │   │   └── product.py      # 商品データモデル
│   │   └── utils/
│   │       ├── image.py        # 画像処理ユーティリティ
│   │       ├── response.py     # レスポンスヘルパー
│   │       └── validation.py   # バリデーション
│   ├── tests/                  # テスト
│   │   ├── unit/               # ユニットテスト
│   │   ├── integration/        # 統合テスト
│   │   └── property/           # プロパティベーステスト
│   ├── template.yaml           # SAM テンプレート
│   └── samconfig.toml          # SAM デプロイ設定
├── frontend/                   # フロントエンド（Next.js）
│   ├── src/
│   │   ├── app/                # App Router ページ
│   │   │   ├── page.tsx            # 商品一覧（ホーム）
│   │   │   ├── login/page.tsx      # サインイン画面
│   │   │   └── products/
│   │   │       ├── new/page.tsx    # 商品追加画面
│   │   │       └── [id]/edit/page.tsx  # 商品編集画面
│   │   ├── components/         # UI コンポーネント
│   │   ├── lib/                # ユーティリティ
│   │   │   ├── api.ts          # API クライアント
│   │   │   ├── auth.ts         # 認証ユーティリティ
│   │   │   └── types.ts       # 型定義
│   │   └── styles/             # グローバルスタイル
│   └── package.json
└── README.md
```

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/products` | 商品一覧取得 |
| POST | `/products` | 商品追加（multipart/form-data） |
| PUT | `/products/{productId}` | 商品更新（multipart/form-data） |
| DELETE | `/products/{productId}` | 商品削除 |

全エンドポイントに Cognito Authorizer による認証が必要です。

## セットアップ

### 前提条件

- Python 3.13
- Node.js 18 以上
- AWS CLI（設定済み）
- AWS SAM CLI

### バックエンドのデプロイ

```bash
cd backend

# ビルド
sam build

# デプロイ（初回はガイド付き）
sam deploy --guided
```

デプロイ後、出力される以下の値をフロントエンドの環境変数に設定します:

- `ApiUrl` → API Gateway エンドポイント URL
- `UserPoolId` → Cognito User Pool ID
- `UserPoolClientId` → Cognito User Pool Client ID
- `CloudFrontDomain` → CloudFront ドメイン名

### フロントエンドの起動

```bash
cd frontend

# 依存関係のインストール
npm install

# 環境変数の設定
cp .env.local.example .env.local
# .env.local を編集し、バックエンドのデプロイ出力値を設定

# 開発サーバーの起動
npm run dev
```

### 環境変数（フロントエンド）

| 変数名 | 説明 |
|--------|------|
| `NEXT_PUBLIC_COGNITO_USER_POOL_ID` | Cognito User Pool ID |
| `NEXT_PUBLIC_COGNITO_CLIENT_ID` | Cognito User Pool Client ID |
| `NEXT_PUBLIC_COGNITO_REGION` | Cognito リージョン（例: ap-northeast-1） |
| `NEXT_PUBLIC_API_BASE_URL` | API Gateway エンドポイント URL |
| `NEXT_PUBLIC_CLOUDFRONT_DOMAIN` | CloudFront ドメイン名 |

## テスト

```bash
cd backend

# 依存関係のインストール
pip install -r requirements-dev.txt

# ユニットテストの実行
pytest tests/unit/ -v
```

## バリデーションルール

| 項目 | ルール |
|------|--------|
| 商品名称 | 必須、1〜200 文字 |
| 価格 | 必須、0 以上の整数 |
| 商品概要 | 任意、最大 2000 文字 |
| 商品画像 | 任意、JPEG / PNG / WebP、最大 5MB |

## デプロイリージョン

デフォルトのデプロイリージョンは `ap-northeast-1`（東京）です。  
`backend/samconfig.toml` の `region` パラメータで変更できます。
