"""商品一覧取得Lambda関数ハンドラ"""

import logging
import os

import boto3

from src.models.product import Product
from src.utils.response import handle_exceptions, success_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数から設定値を取得
PRODUCTS_TABLE_NAME = os.environ.get("PRODUCTS_TABLE_NAME", "")
CLOUDFRONT_DOMAIN = os.environ.get("CLOUDFRONT_DOMAIN", "")

# DynamoDBリソースの初期化
dynamodb = boto3.resource("dynamodb")


def _generate_image_url(image_key: str | None) -> str | None:
    """商品画像のCloudFront URLを生成する

    imageKeyが存在する場合はCloudFront経由のURLを返し、
    存在しない場合はNoneを返す。

    Args:
        image_key: S3オブジェクトキー（Noneの場合あり）

    Returns:
        str | None: CloudFront URL、またはNone
    """
    if not image_key:
        return None
    return f"https://{CLOUDFRONT_DOMAIN}/{image_key}"


def _product_to_response(product: Product) -> dict:
    """ProductオブジェクトをAPIレスポンス形式に変換する

    imageKeyからCloudFront URLを生成し、レスポンス用の辞書を返す。

    Args:
        product: 商品情報オブジェクト

    Returns:
        dict: APIレスポンス用の商品情報辞書
    """
    return {
        "productId": product.product_id,
        "productName": product.product_name,
        "price": product.price,
        "description": product.description,
        "imageUrl": _generate_image_url(product.image_key),
        "createdAt": product.created_at,
        "updatedAt": product.updated_at,
    }


@handle_exceptions
def handler(event, context):
    """商品一覧取得ハンドラ

    DynamoDBから全商品情報を取得し、CloudFront URLを付与して返却する。

    Args:
        event: API Gatewayイベント
        context: Lambdaコンテキスト

    Returns:
        dict: 商品一覧を含むAPIレスポンス
    """
    logger.info("商品一覧取得リクエストを受信")

    # DynamoDBテーブルから全商品を取得
    table = dynamodb.Table(PRODUCTS_TABLE_NAME)
    response = table.scan()
    items = response.get("Items", [])

    # ページネーション対応（全件取得）
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    # 商品データをレスポンス形式に変換
    products = [_product_to_response(Product.from_dict(item)) for item in items]

    logger.info(f"商品一覧取得完了: {len(products)}件")

    return success_response(200, {"products": products})
