'use client';

/**
 * 商品入力フォームコンポーネント
 * 商品追加・編集共用のフォーム
 * クライアントサイドバリデーション、画像プレビュー機能を提供する
 */

import { useState, useRef, FormEvent, ChangeEvent } from 'react';
import { ProductFormData } from '../lib/types';

/** フォーム初期値（編集時に使用） */
interface InitialData {
  productName: string;
  price: number;
  description?: string;
  imageUrl?: string;
}

interface ProductFormProps {
  /** 編集時の初期値（未指定の場合は新規追加モード） */
  initialData?: InitialData;
  /** フォーム送信時のコールバック */
  onSubmit: (data: ProductFormData) => Promise<void>;
  /** 送信ボタンのラベル */
  submitLabel?: string;
}

/** バリデーションエラー */
interface FormErrors {
  productName?: string;
  price?: string;
  description?: string;
}

export default function ProductForm({
  initialData,
  onSubmit,
  submitLabel = '保存',
}: ProductFormProps) {
  const [productName, setProductName] = useState(initialData?.productName || '');
  const [price, setPrice] = useState(
    initialData?.price !== undefined ? String(initialData.price) : ''
  );
  const [description, setDescription] = useState(initialData?.description || '');
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(
    initialData?.imageUrl || null
  );
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  /** バリデーション実行 */
  const validate = (): boolean => {
    const newErrors: FormErrors = {};

    // 商品名称: 必須、1〜200文字
    const trimmedName = productName.trim();
    if (!trimmedName) {
      newErrors.productName = '商品名称は必須です';
    } else if (trimmedName.length > 200) {
      newErrors.productName = '商品名称は200文字以内で入力してください';
    }

    // 価格: 必須、0以上の整数
    if (price === '') {
      newErrors.price = '価格は必須です';
    } else {
      const priceNum = Number(price);
      if (!Number.isInteger(priceNum) || priceNum < 0) {
        newErrors.price = '価格は0以上の整数で入力してください';
      }
    }

    // 商品概要: 最大2000文字
    if (description.length > 2000) {
      newErrors.description = '商品概要は2000文字以内で入力してください';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /** 画像ファイル選択時の処理 */
  const handleImageChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImage(file);

    // FileReader APIで画像プレビューを生成
    const reader = new FileReader();
    reader.onload = (event) => {
      setImagePreview(event.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  /** 画像選択をクリア */
  const handleClearImage = () => {
    setImage(null);
    setImagePreview(initialData?.imageUrl || null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /** フォーム送信処理 */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const formData: ProductFormData = {
        productName: productName.trim(),
        price: Number(price),
        description: description.trim() || undefined,
        image: image || undefined,
      };
      await onSubmit(formData);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="product-form">
      {/* 商品名称 */}
      <div className="form-group">
        <label htmlFor="productName" className="form-label">
          商品名称<span className="required">*</span>
        </label>
        <input
          id="productName"
          type="text"
          className={`form-input ${errors.productName ? 'error' : ''}`}
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
          placeholder="商品名称を入力"
          maxLength={200}
          disabled={isSubmitting}
        />
        {errors.productName && (
          <p className="form-error">{errors.productName}</p>
        )}
      </div>

      {/* 価格 */}
      <div className="form-group">
        <label htmlFor="price" className="form-label">
          価格（円）<span className="required">*</span>
        </label>
        <input
          id="price"
          type="number"
          className={`form-input ${errors.price ? 'error' : ''}`}
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          placeholder="0"
          min="0"
          step="1"
          disabled={isSubmitting}
        />
        {errors.price && <p className="form-error">{errors.price}</p>}
      </div>

      {/* 商品概要 */}
      <div className="form-group">
        <label htmlFor="description" className="form-label">
          商品概要
        </label>
        <textarea
          id="description"
          className={`form-input form-textarea ${errors.description ? 'error' : ''}`}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="商品の説明を入力（任意）"
          maxLength={2000}
          rows={4}
          disabled={isSubmitting}
        />
        {errors.description && (
          <p className="form-error">{errors.description}</p>
        )}
      </div>

      {/* 商品画像 */}
      <div className="form-group">
        <label htmlFor="image" className="form-label">
          商品画像
        </label>
        <input
          id="image"
          ref={fileInputRef}
          type="file"
          className="form-input"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleImageChange}
          disabled={isSubmitting}
        />
        {imagePreview && (
          <div className="image-preview-wrapper">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imagePreview}
              alt="プレビュー"
              className="image-preview"
            />
            <button
              type="button"
              className="btn btn-secondary clear-image-btn"
              onClick={handleClearImage}
              disabled={isSubmitting}
            >
              画像をクリア
            </button>
          </div>
        )}
      </div>

      {/* 送信ボタン */}
      <div className="form-actions">
        <button
          type="submit"
          className="btn btn-primary submit-button"
          disabled={isSubmitting}
        >
          {isSubmitting && <span className="spinner" />}
          {isSubmitting ? '保存中...' : submitLabel}
        </button>
      </div>

      <style jsx>{`
        .product-form {
          max-width: 600px;
        }
        .form-textarea {
          resize: vertical;
          min-height: 100px;
        }
        .image-preview-wrapper {
          margin-top: 12px;
        }
        .image-preview {
          max-width: 300px;
          max-height: 200px;
          border-radius: var(--radius);
          border: 1px solid var(--color-border);
          object-fit: cover;
        }
        .clear-image-btn {
          display: block;
          margin-top: 8px;
          font-size: 12px;
          padding: 4px 12px;
        }
        .form-actions {
          margin-top: 24px;
        }
        .submit-button {
          padding: 12px 32px;
          font-size: 16px;
        }
      `}</style>
    </form>
  );
}
