'use client';

/**
 * 商品一覧コンポーネント
 * 商品カード一覧を表示し、各商品に編集・削除ボタンを提供する
 */

import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { Product } from '../lib/types';

interface ProductListProps {
  /** 商品一覧データ */
  products: Product[];
  /** 削除ボタン押下時のコールバック */
  onDelete: (product: Product) => void;
}

export default function ProductList({ products, onDelete }: ProductListProps) {
  const router = useRouter();

  // 商品が0件の場合
  if (products.length === 0) {
    return (
      <div className="empty-state">
        <p className="empty-message">商品情報がありません</p>
        <style jsx>{`
          .empty-state {
            text-align: center;
            padding: 60px 24px;
          }
          .empty-message {
            font-size: 16px;
            color: var(--color-text-secondary);
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="product-grid">
      {products.map((product) => (
        <div key={product.productId} className="product-card">
          <div className="product-image-wrapper">
            <Image
              src={product.imageUrl || '/placeholder.png'}
              alt={product.productName}
              width={300}
              height={200}
              className="product-image"
              style={{ objectFit: 'cover', width: '100%', height: 'auto' }}
              unoptimized={!product.imageUrl}
            />
          </div>
          <div className="product-info">
            <h3 className="product-name">{product.productName}</h3>
            <p className="product-price">¥{product.price.toLocaleString()}</p>
            {product.description && (
              <p className="product-description">{product.description}</p>
            )}
          </div>
          <div className="product-actions">
            <button
              className="btn btn-secondary"
              onClick={() => router.push(`/products/${product.productId}/edit`)}
            >
              編集
            </button>
            <button
              className="btn btn-danger"
              onClick={() => onDelete(product)}
            >
              削除
            </button>
          </div>
        </div>
      ))}

      <style jsx>{`
        .product-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 24px;
        }
        .product-card {
          background-color: var(--color-surface);
          border-radius: var(--radius);
          box-shadow: var(--shadow);
          overflow: hidden;
          display: flex;
          flex-direction: column;
          transition: box-shadow 0.2s;
        }
        .product-card:hover {
          box-shadow: var(--shadow-md);
        }
        .product-image-wrapper {
          width: 100%;
          height: 200px;
          overflow: hidden;
          background-color: #f1f5f9;
        }
        .product-info {
          padding: 16px;
          flex: 1;
        }
        .product-name {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 8px;
          color: var(--color-text);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .product-price {
          font-size: 18px;
          font-weight: 700;
          color: var(--color-primary);
          margin-bottom: 8px;
        }
        .product-description {
          font-size: 13px;
          color: var(--color-text-secondary);
          line-height: 1.5;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        .product-actions {
          padding: 12px 16px;
          border-top: 1px solid var(--color-border);
          display: flex;
          gap: 8px;
          justify-content: flex-end;
        }
      `}</style>
    </div>
  );
}
