/**
 * 認証ユーティリティ
 * Amazon Cognito USER_PASSWORD_AUTH フローによるサインイン・サインアウト機能を提供する
 */

import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
} from 'amazon-cognito-identity-js';
import { AuthResult } from './types';

// Cognito設定（環境変数から取得）
const USER_POOL_ID = process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID || '';
const CLIENT_ID = process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID || '';

// sessionStorageのキー定数
const TOKEN_KEYS = {
  ID_TOKEN: 'idToken',
  ACCESS_TOKEN: 'accessToken',
  REFRESH_TOKEN: 'refreshToken',
} as const;

/**
 * CognitoUserPoolインスタンスを取得する
 */
function getUserPool(): CognitoUserPool {
  return new CognitoUserPool({
    UserPoolId: USER_POOL_ID,
    ClientId: CLIENT_ID,
  });
}

/**
 * トークンをsessionStorageに保存する
 */
function saveTokens(result: AuthResult): void {
  sessionStorage.setItem(TOKEN_KEYS.ID_TOKEN, result.idToken);
  sessionStorage.setItem(TOKEN_KEYS.ACCESS_TOKEN, result.accessToken);
  sessionStorage.setItem(TOKEN_KEYS.REFRESH_TOKEN, result.refreshToken);
}

/**
 * sessionStorageからトークンを削除する
 */
function clearTokens(): void {
  sessionStorage.removeItem(TOKEN_KEYS.ID_TOKEN);
  sessionStorage.removeItem(TOKEN_KEYS.ACCESS_TOKEN);
  sessionStorage.removeItem(TOKEN_KEYS.REFRESH_TOKEN);
}

/**
 * Cognito USER_PASSWORD_AUTH フローでサインインする
 * @param email メールアドレス
 * @param password パスワード
 * @returns 認証結果（IDトークン、アクセストークン、リフレッシュトークン）
 * @throws 認証失敗時にエラーをスロー
 */
export async function signIn(
  email: string,
  password: string
): Promise<AuthResult> {
  const userPool = getUserPool();

  const cognitoUser = new CognitoUser({
    Username: email,
    Pool: userPool,
  });

  const authenticationDetails = new AuthenticationDetails({
    Username: email,
    Password: password,
  });

  return new Promise<AuthResult>((resolve, reject) => {
    // USER_PASSWORD_AUTH フローを明示的に指定する
    cognitoUser.setAuthenticationFlowType('USER_PASSWORD_AUTH');
    cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: (session) => {
        const result: AuthResult = {
          idToken: session.getIdToken().getJwtToken(),
          accessToken: session.getAccessToken().getJwtToken(),
          refreshToken: session.getRefreshToken().getToken(),
        };
        // トークンをsessionStorageに保存
        saveTokens(result);
        resolve(result);
      },
      onFailure: (err) => {
        reject(new Error(err.message || '認証に失敗しました'));
      },
    });
  });
}

/**
 * サインアウトする
 * GlobalSignOutを実行し、sessionStorageからトークンを削除し、サインイン画面にリダイレクトする
 */
export async function signOut(): Promise<void> {
  const userPool = getUserPool();
  const cognitoUser = userPool.getCurrentUser();

  if (cognitoUser) {
    // GlobalSignOutでサーバー側のセッションも無効化
    await new Promise<void>((resolve) => {
      cognitoUser.globalSignOut({
        onSuccess: () => resolve(),
        onFailure: () => resolve(), // エラーでもローカルのクリーンアップは実行
      });
    });
  }

  // sessionStorageからトークンを削除
  clearTokens();

  // サインイン画面にリダイレクト
  window.location.href = '/login';
}

/**
 * sessionStorageからIDトークンを取得する
 * @returns IDトークン文字列、未認証の場合はnull
 */
export function getIdToken(): string | null {
  if (typeof window === 'undefined') return null;
  return sessionStorage.getItem(TOKEN_KEYS.ID_TOKEN);
}

/**
 * 認証状態を確認する
 * @returns トークンが存在する場合true
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return sessionStorage.getItem(TOKEN_KEYS.ID_TOKEN) !== null;
}
