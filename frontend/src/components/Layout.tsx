'use client';

/**
 * 共通レイアウトコンポーネント
 * ヘッダー（アプリ名「商品管理」、サインアウトボタン）とメインコンテンツエリアを提供する
 */

import { useState } from 'react';
import { signOut } from '../lib/auth';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [isSigningOut, setIsSigningOut] = useState(false);

  /** サインアウト処理 */
  const handleSignOut = async () => {
    setIsSigningOut(true);
    try {
      await signOut();
    } catch {
      // signOut内でリダイレクトされるため、エラーは無視
      setIsSigningOut(false);
    }
  };

  return (
    <div className="layout">
      <header className="layout-header">
        <div className="layout-header-inner">
          <h1 className="layout-title">商品管理</h1>
          <button
            className="btn btn-secondary"
            onClick={handleSignOut}
            disabled={isSigningOut}
          >
            {isSigningOut && <span className="spinner" />}
            サインアウト
          </button>
        </div>
      </header>
      <main className="layout-main">{children}</main>

      <style jsx>{`
        .layout {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }
        .layout-header {
          background-color: var(--color-surface);
          border-bottom: 1px solid var(--color-border);
          box-shadow: var(--shadow);
          position: sticky;
          top: 0;
          z-index: 100;
        }
        .layout-header-inner {
          max-width: 1200px;
          margin: 0 auto;
          padding: 12px 24px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .layout-title {
          font-size: 20px;
          font-weight: 700;
          color: var(--color-text);
        }
        .layout-main {
          flex: 1;
          max-width: 1200px;
          margin: 0 auto;
          padding: 24px;
          width: 100%;
        }
      `}</style>
    </div>
  );
}
