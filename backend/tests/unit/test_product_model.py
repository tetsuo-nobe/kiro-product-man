"""商品モデルの単体テスト"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.models.product import Product


def test_product_to_dict_required_fields():
    """必須フィールドのみの商品をto_dictで変換できること"""
    product = Product(
        product_id="prod-123",
        product_name="テスト商品",
        price=1000,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )
    result = product.to_dict()
    assert result["productId"] == "prod-123"
    assert result["productName"] == "テスト商品"
    assert result["price"] == 1000
    assert "description" not in result
    assert "imageKey" not in result


def test_product_to_dict_all_fields():
    """全フィールドの商品をto_dictで変換できること"""
    product = Product(
        product_id="prod-456",
        product_name="全項目商品",
        price=2000,
        description="商品の説明",
        image_key="products/prod-456/img.jpg",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )
    result = product.to_dict()
    assert result["description"] == "商品の説明"
    assert result["imageKey"] == "products/prod-456/img.jpg"


def test_product_from_dict():
    """DynamoDBアイテムからProductインスタンスを生成できること"""
    data = {
        "productId": "prod-789",
        "productName": "復元商品",
        "price": 3000,
        "description": "復元テスト",
        "imageKey": "products/prod-789/img.png",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }
    product = Product.from_dict(data)
    assert product.product_id == "prod-789"
    assert product.product_name == "復元商品"
    assert product.price == 3000
    assert product.description == "復元テスト"
    assert product.image_key == "products/prod-789/img.png"


def test_product_round_trip():
    """to_dict → from_dict のラウンドトリップが等価であること"""
    original = Product(
        product_id="prod-rt",
        product_name="ラウンドトリップ",
        price=500,
        description="テスト説明",
        image_key="products/prod-rt/img.webp",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )
    restored = Product.from_dict(original.to_dict())
    assert restored.product_id == original.product_id
    assert restored.product_name == original.product_name
    assert restored.price == original.price
    assert restored.description == original.description
    assert restored.image_key == original.image_key
    assert restored.created_at == original.created_at
    assert restored.updated_at == original.updated_at
