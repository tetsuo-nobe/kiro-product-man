'use client';

/**
 * 商品追加画面
 * ProductFormを使用して新規商品を追加する
 * 保存成功時は一覧画面に遷移、失敗時はエラーメッセージを表示する
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '../../../lib/auth';
import { createProduct } from '../../../lib/api';
import { ProductFormData } from '../../../lib/types';
import Layout from '../../../components/Layout';
import ProductForm from '../../../components/ProductForm';

export default function NewProductPage() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    // 未認証時はサインイン画面にリダイレクト
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  /** 商品追加処理 */
  const handleSubmit = async (data: ProductFormData) => {
    setError('');
    setSuccess('');

    try {
      await createProduct(data);
      setSuccess('商品を追加しました');
      // 少し待ってから一覧画面に遷移
      setTimeout(() => {
        router.push('/');
      }, 1000);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : '商品の追加に失敗しました';
      setError(message);
    }
  };

  if (typeof window !== 'undefined' && !isAuthenticated()) {
    return null;
  }

  return (
    <Layout>
      <div className="page-header">
        <h2 className="page-title">商品追加</h2>
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

      <ProductForm onSubmit={handleSubmit} submitLabel="追加" />

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
      `}</style>
    </Layout>
  );
}
