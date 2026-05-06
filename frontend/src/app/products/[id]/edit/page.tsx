'use client';

/**
 * 商品編集画面
 * 既存商品情報をAPIから取得し、ProductFormに初期値として設定する
 * 更新成功時は一覧画面に遷移、失敗時はエラーメッセージを表示する
 */

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { isAuthenticated } from '../../../../lib/auth';
import { listProducts, updateProduct } from '../../../../lib/api';
import { Product, ProductFormData } from '../../../../lib/types';
import Layout from '../../../../components/Layout';
import ProductForm from '../../../../components/ProductForm';

export default function EditProductPage() {
  const router = useRouter();
  const params = useParams();
  const productId = params.id as string;

  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    // 未認証時はサインイン画面にリダイレクト
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    // 商品情報を取得
    const fetchProduct = async () => {
      try {
        const products = await listProducts();
        const found = products.find((p) => p.productId === productId);
        if (found) {
          setProduct(found);
        } else {
          setError('指定された商品が見つかりません');
        }
      } catch (err) {
        const message =
          err instanceof Error ? err.message : '商品情報の取得に失敗しました';
        setError(message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProduct();
  }, [router, productId]);

  /** 商品更新処理 */
  const handleSubmit = async (data: ProductFormData) => {
    setError('');
    setSuccess('');

    try {
      await updateProduct(productId, data);
      setSuccess('商品を更新しました');
      // 少し待ってから一覧画面に遷移
      setTimeout(() => {
        router.push('/');
      }, 1000);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : '商品の更新に失敗しました';
      setError(message);
    }
  };

  if (typeof window !== 'undefined' && !isAuthenticated()) {
    return null;
  }

  return (
    <Layout>
      <div className="page-header">
        <h2 className="page-title">商品編集</h2>
        <button
          className="btn btn-secondary"
          onClick={() => router.push('/')}
        >
          一覧に戻る
        </button>
      </div>

      {success && (
        <div className="message-success" role="status">
          {success}
        </div>
      )}

      {error && (
        <div className="message-error" role="alert">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="loading-state">
          <p>読み込み中...</p>
        </div>
      ) : (
        product && (
          <ProductForm
            initialData={{
              productName: product.productName,
              price: product.price,
              description: product.description,
              imageUrl: product.imageUrl,
            }}
            onSubmit={handleSubmit}
            submitLabel="更新"
          />
        )
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
      `}</style>
    </Layout>
  );
}
