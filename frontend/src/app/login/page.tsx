'use client';

/**
 * サインイン画面
 * メールアドレス・パスワードによるCognito認証を行う
 * 認証成功時は商品一覧画面（/）にリダイレクトする
 */

import { useState, useEffect, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { signIn, isAuthenticated } from '../../lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 既に認証済みの場合は一覧画面にリダイレクト
  useEffect(() => {
    if (isAuthenticated()) {
      router.push('/');
    }
  }, [router]);

  /** サインインフォーム送信処理 */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await signIn(email, password);
      router.push('/');
    } catch (err) {
      const message = err instanceof Error ? err.message : '認証に失敗しました';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">商品管理</h1>
        <p className="login-subtitle">サインイン</p>

        {error && (
          <div className="message-error" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              メールアドレス
            </label>
            <input
              id="email"
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="example@email.com"
              required
              disabled={isLoading}
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              パスワード
            </label>
            <input
              id="password"
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="パスワードを入力"
              required
              disabled={isLoading}
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary login-button"
            disabled={isLoading}
          >
            {isLoading && <span className="spinner" />}
            {isLoading ? 'サインイン中...' : 'サインイン'}
          </button>
        </form>
      </div>

      <style jsx>{`
        .login-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
        }
        .login-card {
          background-color: var(--color-surface);
          border-radius: var(--radius);
          box-shadow: var(--shadow-md);
          padding: 40px;
          width: 100%;
          max-width: 400px;
        }
        .login-title {
          font-size: 24px;
          font-weight: 700;
          text-align: center;
          margin-bottom: 4px;
          color: var(--color-text);
        }
        .login-subtitle {
          font-size: 14px;
          text-align: center;
          color: var(--color-text-secondary);
          margin-bottom: 24px;
        }
        .login-button {
          width: 100%;
          padding: 12px;
          font-size: 16px;
          margin-top: 8px;
        }
      `}</style>
    </div>
  );
}
