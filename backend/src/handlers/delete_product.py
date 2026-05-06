"""商品削除Lambda関数ハンドラ"""

import logging
import os

import boto3

from src.models.product import Product
from src.utils.response import handle_exceptions, success_response
from src.utils.validation import NotFoundError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数から設定値を取得
PRODUCTS_TABLE_NAME = os.environ.get("PRODUCTS_TABLE_NAME", "")
IMAGE_BUCKET_NAME = os.environ.get("IMAGE_BUCKET_NAME", "")

# AWSリソースの初期化
dynamodb = boto3.resource("dynamodb")
s3_client = boto3.client("s3")


@handle_exceptions
def handler(event, context):
    """商品削除ハンドラ

    パスパラメータから商品IDを取得し、関連する画像とDynamoDBレコードを削除する。

    Args:
        event: API Gatewayイベント
        context: Lambdaコンテキスト

    Returns:
        dict: 削除成功メッセージを含むAPIレスポンス（200 OK）
    """
    logger.info("商品削除リクエストを受信")

    # パスパラメータから商品IDを取得
    product_id = event["pathParameters"]["productId"]
    logger.info(f"削除対象商品ID: {product_id}")

    # DynamoDBから既存商品情報を取得（存在確認と画像キーの取得）
    table = dynamodb.Table(PRODUCTS_TABLE_NAME)
    response = table.get_item(Key={"productId": product_id})

    if "Item" not in response:
        raise NotFoundError("指定された商品が見つかりません")

    # 既存商品情報をProductオブジェクトに変換
    existing_product = Product.from_dict(response["Item"])

    # 画像が存在する場合、S3から削除
    if existing_product.image_key:
        s3_client.delete_object(
            Bucket=IMAGE_BUCKET_NAME,
            Key=existing_product.image_key,
        )
        logger.info(f"商品画像削除完了: {existing_product.image_key}")

    # DynamoDBから商品情報を削除
    table.delete_item(Key={"productId": product_id})
    logger.info(f"商品情報削除完了: {product_id}")

    return success_response(200, {"message": "商品を削除しました"})
