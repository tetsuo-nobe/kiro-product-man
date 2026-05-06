"""バリデーションモジュールの単体テスト"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest
from src.utils.validation import ValidationError, NotFoundError, validate_product_data


def test_valid_product_data():
    """有効な商品データがバリデーションを通過すること"""
    data = {"productName": "テスト商品", "price": 1000}
    validate_product_data(data)  # 例外が発生しないこと


def test_valid_product_data_with_description():
    """商品概要付きの有効なデータがバリデーションを通過すること"""
    data = {"productName": "テスト商品", "price": 1000, "description": "説明文"}
    validate_product_data(data)


def test_missing_product_name():
    """商品名称が未指定の場合にValidationErrorが発生すること"""
    data = {"price": 1000}
    with pytest.raises(ValidationError, match="商品名称は必須です"):
        validate_product_data(data)


def test_empty_product_name():
    """商品名称が空文字の場合にValidationErrorが発生すること"""
    data = {"productName": "", "price": 1000}
    with pytest.raises(ValidationError, match="商品名称は必須です"):
        validate_product_data(data)


def test_whitespace_only_product_name():
    """商品名称が空白のみの場合にValidationErrorが発生すること"""
    data = {"productName": "   ", "price": 1000}
    with pytest.raises(ValidationError, match="商品名称は必須です"):
        validate_product_data(data)


def test_product_name_too_long():
    """商品名称が200文字を超える場合にValidationErrorが発生すること"""
    data = {"productName": "あ" * 201, "price": 1000}
    with pytest.raises(ValidationError, match="200文字以内"):
        validate_product_data(data)


def test_missing_price():
    """価格が未指定の場合にValidationErrorが発生すること"""
    data = {"productName": "テスト商品"}
    with pytest.raises(ValidationError, match="価格は必須です"):
        validate_product_data(data)


def test_negative_price():
    """価格が負数の場合にValidationErrorが発生すること"""
    data = {"productName": "テスト商品", "price": -1}
    with pytest.raises(ValidationError, match="0以上の整数"):
        validate_product_data(data)


def test_zero_price():
    """価格が0の場合にバリデーションを通過すること"""
    data = {"productName": "テスト商品", "price": 0}
    validate_product_data(data)


def test_description_too_long():
    """商品概要が2000文字を超える場合にValidationErrorが発生すること"""
    data = {"productName": "テスト商品", "price": 1000, "description": "あ" * 2001}
    with pytest.raises(ValidationError, match="2000文字以内"):
        validate_product_data(data)


def test_validation_error_is_exception():
    """ValidationErrorがExceptionのサブクラスであること"""
    assert issubclass(ValidationError, Exception)


def test_not_found_error_is_exception():
    """NotFoundErrorがExceptionのサブクラスであること"""
    assert issubclass(NotFoundError, Exception)
