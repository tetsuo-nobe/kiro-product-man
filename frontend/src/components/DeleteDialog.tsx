'use client';

/**
 * 削除確認ダイアログコンポーネント
 * 商品削除前に確認メッセージを表示し、確認/キャンセル操作を提供する
 */

import { useState } from 'react';
import { deleteProduct } from '../lib/api';
import { Product } from '../lib/types';

interface DeleteDialogProps {
  /** 削除対象の商品 */
  product: Product;
  /** 削除完了時のコールバック */
  onComplete: () => void;
  /** キャンセル時のコールバック */
  onCancel: () => void;
}

export default function DeleteDialog({
  product,
  onComplete,
  onCancel,
}: DeleteDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState('');

  /** 削除実行処理 */
  const handleDelete = async () => {
    setIsDeleting(true);
    setError('');

    try {
      await deleteProduct(product.productId);
      onComplete();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : '商品の削除に失敗しました';
      setError(message);
      setIsDeleting(false);
    }
  };

  return (
    <div className="dialog-overlay" onClick={onCancel}>
      <div
        className="dialog-content"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-dialog-title"
      >
        <h3 id="delete-dialog-title" className="dialog-title">
          削除確認
        </h3>
        <p className="dialog-message">
          「{product.productName}」を削除しますか？
        </p>
        <p className="dialog-warning">この操作は取り消せません。</p>

        {error && (
          <div className="message-error" role="alert">
            {error}
          </div>
        )}

        <div className="dialog-actions">
          <button
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={isDeleting}
          >
            キャンセル
          </button>
          <button
            className="btn btn-danger"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting && <span className="spinner" />}
            {isDeleting ? '削除中...' : '削除する'}
          </button>
        </div>
      </div>

      <style jsx>{`
        .dialog-overlay {
          position: fixed;
          inset: 0;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 24px;
        }
        .dialog-content {
          background-color: var(--color-surface);
          border-radius: var(--radius);
          box-shadow: var(--shadow-md);
          padding: 24px;
          width: 100%;
          max-width: 400px;
        }
        .dialog-title {
          font-size: 18px;
          font-weight: 700;
          margin-bottom: 12px;
        }
        .dialog-message {
          font-size: 14px;
          color: var(--color-text);
          margin-bottom: 8px;
        }
        .dialog-warning {
          font-size: 13px;
          color: var(--color-text-secondary);
          margin-bottom: 16px;
        }
        .dialog-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          margin-top: 16px;
        }
      `}</style>
    </div>
  );
}
