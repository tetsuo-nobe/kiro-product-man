/**
 * フロントエンド型定義
 * 商品情報管理アプリケーションで使用する共通型を定義する
 */

/** 商品情報インターフェース */
export interface Product {
  /** 商品ID（UUID v4形式: prod-{uuid}） */
  productId: string;
  /** 商品名称 */
  productName: string;
  /** 価格（整数、円単位） */
  price: number;
  /** 商品概要（任意） */
  description?: string;
  /** 商品画像URL（CloudFront経由、任意） */
  imageUrl?: string;
  /** 作成日時（ISO 8601形式） */
  createdAt: string;
  /** 更新日時（ISO 8601形式） */
  updatedAt: string;
}

/** 商品フォームデータインターフェース */
export interface ProductFormData {
  /** 商品名称（必須、1〜200文字） */
  productName: string;
  /** 価格（必須、0以上の整数） */
  price: number;
  /** 商品概要（任意、最大2000文字） */
  description?: string;
  /** 商品画像ファイル（任意、JPEG/PNG/WebP） */
  image?: File;
}

/** 認証結果インターフェース */
export interface AuthResult {
  /** IDトークン（API認証に使用） */
  idToken: string;
  /** アクセストークン */
  accessToken: string;
  /** リフレッシュトークン */
  refreshToken: string;
}

/** APIエラーレスポンスインターフェース */
export interface ApiError {
  /** エラー種別（例: ValidationError, NotFoundError） */
  error: string;
  /** エラーメッセージ */
  message: string;
}
