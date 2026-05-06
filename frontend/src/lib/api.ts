/**
 * APIクライアント
 * バックエンドREST APIとの通信を担当する
 * 認証トークンの自動付与、401レスポンス時のリダイレクト処理を含む
 */

import { Product, ProductFormData, ApiError } from './types';
import { getIdToken } from './auth';

// API基本URL（環境変数から取得）
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

/**
 * ネットワークエラー
 * fetch自体が失敗した場合（ネットワーク接続不可等）にスローされる
 */
export class NetworkError extends Error {
  constructor(message: string = 'ネットワーク接続を確認してください') {
    super(message);
    this.name = 'NetworkError';
  }
}

/**
 * APIリクエストエラー
 * APIからエラーレスポンスが返却された場合にスローされる
 */
export class ApiRequestError extends Error {
  /** HTTPステータスコード */
  public readonly statusCode: number;
  /** エラー種別 */
  public readonly errorType: string;

  constructor(statusCode: number, message: string, errorType: string = 'ApiError') {
    super(message);
    this.name = 'ApiRequestError';
    this.statusCode = statusCode;
    this.errorType = errorType;
  }
}

/**
 * トークンをクリアしてサインイン画面にリダイレクトする
 */
function handleUnauthorized(): void {
  sessionStorage.removeItem('idToken');
  sessionStorage.removeItem('accessToken');
  sessionStorage.removeItem('refreshToken');
  window.location.href = '/login';
}

/**
 * 認証付きAPIリクエストを実行する
 * @param path APIパス（例: /products）
 * @param options fetchオプション
 * @returns レスポンスデータ
 * @throws NetworkError ネットワーク接続エラー時
 * @throws ApiRequestError APIエラーレスポンス時
 */
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getIdToken();
  if (!token) {
    handleUnauthorized();
    throw new ApiRequestError(401, '認証が必要です', 'AuthError');
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        ...options?.headers,
      },
    });
  } catch (error) {
    throw new NetworkError();
  }

  // 401レスポンス時はトークン削除してリダイレクト
  if (response.status === 401) {
    handleUnauthorized();
    throw new ApiRequestError(401, '認証が期限切れです', 'AuthError');
  }

  // その他のエラーレスポンス
  if (!response.ok) {
    let errorData: ApiError;
    try {
      errorData = await response.json();
    } catch {
      throw new ApiRequestError(
        response.status,
        'サーバーエラーが発生しました',
        'UnknownError'
      );
    }
    throw new ApiRequestError(response.status, errorData.message, errorData.error);
  }

  return await response.json() as T;
}

/**
 * 商品一覧を取得する
 * @returns 商品情報の配列
 */
export async function listProducts(): Promise<Product[]> {
  const data = await request<{ products: Product[] }>('/products');
  return data.products;
}

/**
 * 商品を追加する（multipart/form-data）
 * @param data 商品フォームデータ
 * @returns 作成された商品情報
 */
export async function createProduct(data: ProductFormData): Promise<Product> {
  const formData = new FormData();
  formData.append('productName', data.productName);
  formData.append('price', String(data.price));
  if (data.description) {
    formData.append('description', data.description);
  }
  if (data.image) {
    formData.append('image', data.image);
  }

  const result = await request<{ product: Product }>('/products', {
    method: 'POST',
    body: formData,
  });
  return result.product;
}

/**
 * 商品を更新する（multipart/form-data）
 * @param productId 商品ID
 * @param data 商品フォームデータ
 * @returns 更新された商品情報
 */
export async function updateProduct(
  productId: string,
  data: ProductFormData
): Promise<Product> {
  const formData = new FormData();
  formData.append('productName', data.productName);
  formData.append('price', String(data.price));
  if (data.description) {
    formData.append('description', data.description);
  }
  if (data.image) {
    formData.append('image', data.image);
  }

  const result = await request<{ product: Product }>(`/products/${productId}`, {
    method: 'PUT',
    body: formData,
  });
  return result.product;
}

/**
 * 商品を削除する
 * @param productId 商品ID
 */
export async function deleteProduct(productId: string): Promise<void> {
  await request<{ message: string }>(`/products/${productId}`, {
    method: 'DELETE',
  });
}
