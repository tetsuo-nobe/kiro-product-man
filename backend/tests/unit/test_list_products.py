"""商品一覧取得ハンドラの単体テスト"""

import json
import os
from unittest.mock import patch

import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def env_vars():
    """テスト用環境変数を設定する"""
    os.environ["PRODUCTS_TABLE_NAME"] = "test-products-table"
    os.environ["CLOUDFRONT_DOMAIN"] = "d1234567890.cloudfront.net"
    yield
    del os.environ["PRODUCTS_TABLE_NAME"]
    del os.environ["CLOUDFRONT_DOMAIN"]


@pytest.fixture
def dynamodb_table():
    """テスト用DynamoDBテーブルを作成する"""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
        table = dynamodb.create_table(
            TableName="test-products-table",
            KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "productId", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        table.meta.client.get_waiter("table_exists").wait(
            TableName="test-products-table"
        )
        yield table


@mock_aws
def test_handler_returns_empty_list_when_no_products(env_vars):
    """商品が0件の場合、空のリストを返す"""
    # テーブル作成
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    dynamodb.create_table(
        TableName="test-products-table",
        KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "productId", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    # ハンドラのインポート（環境変数設定後）
    from src.handlers.list_products import handler

    # モジュール内のdynamodbリソースを再設定
    import src.handlers.list_products as module

    module.dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    module.PRODUCTS_TABLE_NAME = "test-products-table"
    module.CLOUDFRONT_DOMAIN = "d1234567890.cloudfront.net"

    response = handler({}, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["products"] == []


@mock_aws
def test_handler_returns_products_with_image_url(env_vars):
    """画像キーがある商品にはCloudFront URLが設定される"""
    # テーブル作成とデータ投入
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    table = dynamodb.create_table(
        TableName="test-products-table",
        KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "productId", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.put_item(
        Item={
            "productId": "prod-001",
            "productName": "テスト商品",
            "price": 1980,
            "description": "テスト商品の説明",
            "imageKey": "products/prod-001/img-abc.jpg",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
        }
    )

    from src.handlers.list_products import handler

    import src.handlers.list_products as module

    module.dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    module.PRODUCTS_TABLE_NAME = "test-products-table"
    module.CLOUDFRONT_DOMAIN = "d1234567890.cloudfront.net"

    response = handler({}, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body["products"]) == 1

    product = body["products"][0]
    assert product["productId"] == "prod-001"
    assert product["productName"] == "テスト商品"
    assert product["price"] == 1980
    assert product["description"] == "テスト商品の説明"
    assert (
        product["imageUrl"]
        == "https://d1234567890.cloudfront.net/products/prod-001/img-abc.jpg"
    )
    assert product["createdAt"] == "2024-01-01T00:00:00Z"
    assert product["updatedAt"] == "2024-01-01T00:00:00Z"


@mock_aws
def test_handler_returns_null_image_url_when_no_image_key(env_vars):
    """画像キーがない商品のimageUrlはnullになる"""
    # テーブル作成とデータ投入
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    table = dynamodb.create_table(
        TableName="test-products-table",
        KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "productId", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.put_item(
        Item={
            "productId": "prod-002",
            "productName": "画像なし商品",
            "price": 500,
            "createdAt": "2024-01-02T00:00:00Z",
            "updatedAt": "2024-01-02T00:00:00Z",
        }
    )

    from src.handlers.list_products import handler

    import src.handlers.list_products as module

    module.dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    module.PRODUCTS_TABLE_NAME = "test-products-table"
    module.CLOUDFRONT_DOMAIN = "d1234567890.cloudfront.net"

    response = handler({}, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body["products"]) == 1

    product = body["products"][0]
    assert product["productId"] == "prod-002"
    assert product["imageUrl"] is None


@mock_aws
def test_handler_returns_multiple_products(env_vars):
    """複数商品が正しく返却される"""
    # テーブル作成とデータ投入
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    table = dynamodb.create_table(
        TableName="test-products-table",
        KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "productId", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.put_item(
        Item={
            "productId": "prod-001",
            "productName": "商品A",
            "price": 1000,
            "imageKey": "products/prod-001/img.jpg",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
        }
    )
    table.put_item(
        Item={
            "productId": "prod-002",
            "productName": "商品B",
            "price": 2000,
            "createdAt": "2024-01-02T00:00:00Z",
            "updatedAt": "2024-01-02T00:00:00Z",
        }
    )

    from src.handlers.list_products import handler

    import src.handlers.list_products as module

    module.dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    module.PRODUCTS_TABLE_NAME = "test-products-table"
    module.CLOUDFRONT_DOMAIN = "d1234567890.cloudfront.net"

    response = handler({}, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body["products"]) == 2

    # 全商品に必須フィールドが含まれることを確認
    for product in body["products"]:
        assert "productId" in product
        assert "productName" in product
        assert "price" in product
        assert "imageUrl" in product
        assert "createdAt" in product
        assert "updatedAt" in product


@mock_aws
def test_handler_includes_cors_headers(env_vars):
    """レスポンスにCORSヘッダーが含まれる"""
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    dynamodb.create_table(
        TableName="test-products-table",
        KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "productId", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    from src.handlers.list_products import handler

    import src.handlers.list_products as module

    module.dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    module.PRODUCTS_TABLE_NAME = "test-products-table"
    module.CLOUDFRONT_DOMAIN = "d1234567890.cloudfront.net"

    response = handler({}, None)

    assert response["headers"]["Access-Control-Allow-Origin"] == "*"
    assert "Content-Type" in response["headers"]


@mock_aws
def test_handler_returns_description_as_none_when_not_set(env_vars):
    """descriptionが未設定の商品はdescriptionがnullで返る"""
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    table = dynamodb.create_table(
        TableName="test-products-table",
        KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "productId", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.put_item(
        Item={
            "productId": "prod-003",
            "productName": "説明なし商品",
            "price": 300,
            "createdAt": "2024-01-03T00:00:00Z",
            "updatedAt": "2024-01-03T00:00:00Z",
        }
    )

    from src.handlers.list_products import handler

    import src.handlers.list_products as module

    module.dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    module.PRODUCTS_TABLE_NAME = "test-products-table"
    module.CLOUDFRONT_DOMAIN = "d1234567890.cloudfront.net"

    response = handler({}, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    product = body["products"][0]
    assert product["description"] is None
