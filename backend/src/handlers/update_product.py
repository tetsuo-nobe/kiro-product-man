"""商品更新Lambda関数ハンドラ"""

import base64
import logging
import os
from datetime import datetime, timezone
from io import BytesIO

import boto3

from src.models.product import Product
from src.utils.image import generate_image_key, validate_image_format, validate_image_size
from src.utils.response import handle_exceptions, success_response
from src.utils.validation import NotFoundError, ValidationError, validate_product_data

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数から設定値を取得
PRODUCTS_TABLE_NAME = os.environ.get("PRODUCTS_TABLE_NAME", "")
IMAGE_BUCKET_NAME = os.environ.get("IMAGE_BUCKET_NAME", "")
CLOUDFRONT_DOMAIN = os.environ.get("CLOUDFRONT_DOMAIN", "")

# AWSリソースの初期化
dynamodb = boto3.resource("dynamodb")
s3_client = boto3.client("s3")


def _parse_multipart_data(event: dict) -> tuple[dict, dict | None]:
    """multipart/form-dataリクエストボディをパースする

    API Gatewayから送信されるmultipart/form-dataを解析し、
    フォームフィールドとファイルデータを抽出する。

    Args:
        event: API Gatewayイベント

    Returns:
        tuple: (フォームフィールド辞書, ファイル情報辞書またはNone)
            ファイル情報辞書: {"content": bytes, "content_type": str, "filename": str}

    Raises:
        ValidationError: Content-Typeが不正、またはパースに失敗した場合
    """
    # Content-Typeヘッダーからboundaryを取得
    headers = event.get("headers", {})
    content_type = headers.get("content-type") or headers.get("Content-Type", "")

    if "multipart/form-data" not in content_type:
        raise ValidationError("Content-Typeはmultipart/form-dataである必要があります")

    # boundaryの抽出
    boundary = None
    for part in content_type.split(";"):
        part = part.strip()
        if part.startswith("boundary="):
            boundary = part[len("boundary="):]
            break

    if not boundary:
        raise ValidationError("multipart/form-dataのboundaryが見つかりません")

    # リクエストボディの取得（base64デコード対応）
    body = event.get("body", "")
    if event.get("isBase64Encoded", False):
        body_bytes = base64.b64decode(body)
    else:
        if isinstance(body, str):
            body_bytes = body.encode("utf-8")
        else:
            body_bytes = body

    # multipartデータのパース
    fields = {}
    file_data = None

    # boundaryでパートを分割
    boundary_bytes = boundary.encode("utf-8") if isinstance(boundary, str) else boundary
    delimiter = b"--" + boundary_bytes

    parts = body_bytes.split(delimiter)

    for part in parts:
        # 空パートや終端マーカーをスキップ
        if not part or part == b"--" or part == b"--\r\n":
            continue

        # パート先頭の改行を除去（boundaryの直後に\r\nが付く）
        if part.startswith(b"\r\n"):
            part = part[2:]
        elif part.startswith(b"\n"):
            part = part[1:]

        # 終端マーカーをスキップ
        if part.startswith(b"--"):
            continue

        # ヘッダーとボディを分離
        if b"\r\n\r\n" in part:
            header_section, body_section = part.split(b"\r\n\r\n", 1)
        elif b"\n\n" in part:
            header_section, body_section = part.split(b"\n\n", 1)
        else:
            continue

        # 末尾の改行を除去
        if body_section.endswith(b"\r\n"):
            body_section = body_section[:-2]
        elif body_section.endswith(b"\n"):
            body_section = body_section[:-1]

        # ヘッダーの解析
        header_text = header_section.decode("utf-8", errors="replace")
        headers_dict = {}
        for line in header_text.split("\r\n"):
            if not line.strip():
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                headers_dict[key.strip().lower()] = value.strip()

        # Content-Dispositionからフィールド名とファイル名を取得
        disposition = headers_dict.get("content-disposition", "")
        field_name = None
        filename = None

        for item in disposition.split(";"):
            item = item.strip()
            if item.startswith("name="):
                field_name = item[5:].strip('"').strip("'")
            elif item.startswith("filename="):
                filename = item[9:].strip('"').strip("'")

        if not field_name:
            continue

        # ファイルフィールドの場合
        if filename:
            part_content_type = headers_dict.get("content-type", "application/octet-stream")
            file_data = {
                "content": body_section,
                "content_type": part_content_type,
                "filename": filename,
            }
        else:
            # テキストフィールドの場合
            fields[field_name] = body_section.decode("utf-8", errors="replace")

    return fields, file_data


@handle_exceptions
def handler(event, context):
    """商品更新ハンドラ

    パスパラメータから商品IDを取得し、既存商品情報を更新する。
    画像変更がある場合は新画像のアップロードと旧画像の削除を行う。

    Args:
        event: API Gatewayイベント
        context: Lambdaコンテキスト

    Returns:
        dict: 更新された商品情報を含むAPIレスポンス（200 OK）
    """
    logger.info("商品更新リクエストを受信")

    # パスパラメータから商品IDを取得
    product_id = event["pathParameters"]["productId"]
    logger.info(f"更新対象商品ID: {product_id}")

    # DynamoDBから既存商品情報を取得
    table = dynamodb.Table(PRODUCTS_TABLE_NAME)
    response = table.get_item(Key={"productId": product_id})

    if "Item" not in response:
        raise NotFoundError("指定された商品が見つかりません")

    # 既存商品情報をProductオブジェクトに変換
    existing_product = Product.from_dict(response["Item"])

    # multipart/form-dataのパース
    fields, file_data = _parse_multipart_data(event)

    # バリデーション用データの構築
    validation_data = {
        "productName": fields.get("productName", ""),
        "price": fields.get("price"),
        "description": fields.get("description"),
    }

    # バリデーション実行
    validate_product_data(validation_data)

    # 画像処理
    image_key = existing_product.image_key  # デフォルトは既存の画像キーを維持
    old_image_key = existing_product.image_key  # 旧画像キーを保持

    if file_data and file_data.get("content") and file_data.get("filename"):
        file_content = file_data["content"]
        content_type = file_data["content_type"]

        # 画像形式の検証（マジックバイトチェック）
        extension = validate_image_format(content_type, file_content)

        # 画像サイズの検証（最大5MB）
        validate_image_size(file_content)

        # 新しいS3オブジェクトキーの生成
        image_key = generate_image_key(product_id, extension)

        # S3に新画像をアップロード
        s3_client.put_object(
            Bucket=IMAGE_BUCKET_NAME,
            Key=image_key,
            Body=file_content,
            ContentType=content_type,
        )
        logger.info(f"新画像アップロード完了: {image_key}")

        # 旧画像をS3から削除
        if old_image_key:
            s3_client.delete_object(
                Bucket=IMAGE_BUCKET_NAME,
                Key=old_image_key,
            )
            logger.info(f"旧画像削除完了: {old_image_key}")

    # 現在時刻をISO 8601形式で取得（updatedAtのみ更新）
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 更新後のProductインスタンスを作成（createdAtは既存値を維持）
    updated_product = Product(
        product_id=product_id,
        product_name=fields.get("productName", ""),
        price=int(fields.get("price", 0)),
        description=fields.get("description"),
        image_key=image_key,
        created_at=existing_product.created_at,
        updated_at=now,
    )

    # DynamoDBの商品情報を更新
    table.put_item(Item=updated_product.to_dict())
    logger.info(f"商品情報更新完了: {product_id}")

    # CloudFront URLの生成
    image_url = None
    if image_key:
        image_url = f"https://{CLOUDFRONT_DOMAIN}/{image_key}"

    # レスポンスの構築
    response_body = {
        "product": {
            "productId": updated_product.product_id,
            "productName": updated_product.product_name,
            "price": updated_product.price,
            "description": updated_product.description,
            "imageUrl": image_url,
            "createdAt": updated_product.created_at,
            "updatedAt": updated_product.updated_at,
        }
    }

    logger.info(f"商品更新完了: {product_id}")

    return success_response(200, response_body)
