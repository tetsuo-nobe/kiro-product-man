'use client';

/**
 * 商品一覧画面（ホーム）
 * 認証済みユーザーに商品一覧を表示する
 * 未認証時はサインイン画面にリダイレクトする
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '../lib/auth';
import { listProducts } from '../lib/api';
import { Product } from '../lib/types';
import Layout from '../components/Layout';
import ProductList from '../components/ProductList';
import DeleteDialog from '../components/DeleteDialog';

export default function HomePage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<Product | null>(null);
  const [authChecked, setAuthChecked] = useState(false);

  /** 商品一覧を取得する */
  const fetchProducts = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await listProducts();
      setProducts(data);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'データの取得に失敗しました';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // 未認証時はサインイン画面にリダイレクト
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    setAuthChecked(true);
    fetchProducts();
  }, [router, fetchProducts]);

  /** 削除ダイアログを開く */
  const handleDeleteClick = (product: Product) => {
    setDeleteTarget(product);
  };

  /** 削除完了後のコールバック */
  const handleDeleteComplete = () => {
    setDeleteTarget(null);
    fetchProducts();
  };

  /** 削除ダイアログを閉じる */
  const handleDeleteCancel = () => {
    setDeleteTarget(null);
  };

  // 認証チェックが完了するまで何も表示しない
  if (!authChecked) {
    return null;
  }

  return (
    <Layout>
      <div className="page-header">
        <h2 className="page-title">商品一覧</h2>
        <button
          className="btn btn-primary"
          onClick={() => router.push('/products/new')}
        >
          商品を追加
        </button>
      </div>

      {error && (
        <div className="message-error" role="alert">
          <p>{error}</p>
          <button
            className="btn btn-secondary retry-button"
            onClick={fetchProducts}
          >
            再試行
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="loading-state">
          <p>読み込み中...</p>
        </div>
      ) : (
        !error && (
          <ProductList products={products} onDelete={handleDeleteClick} />
        )
      )}

      {deleteTarget && (
        <DeleteDialog
          product={deleteTarget}
          onComplete={handleDeleteComplete}
          onCancel={handleDeleteCancel}
        />
      )}

      <style jsx>{`
        .page-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 24px;
        }
        .page-title {
          font-size: 24px;
          font-weight: 700;
        }
        .loading-state {
          text-align: center;
          padding: 60px 24px;
          color: var(--color-text-secondary);
        }
        .retry-button {
          margin-top: 8px;
        }
      `}</style>
    </Layout>
  );
}
