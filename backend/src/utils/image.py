"""画像処理ユーティリティモジュール"""

import uuid

from src.utils.validation import ValidationError

# 最大ファイルサイズ: 5MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024

# サポートする画像形式とマジックバイト
IMAGE_MAGIC_BYTES = {
    "jpeg": [
        b"\xff\xd8\xff",  # JPEG/JFIF/Exif
    ],
    "png": [
        b"\x89PNG\r\n\x1a\n",  # PNG
    ],
    "webp": [
        b"RIFF",  # WebP (先頭4バイト、追加で8バイト目以降に"WEBP"を確認)
    ],
}

# Content-Typeと拡張子のマッピング
CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


def validate_image_format(content_type: str, file_content: bytes) -> str:
    """画像ファイル形式をマジックバイトで検証する

    Content-Typeとファイルの実際のマジックバイトの両方を検証し、
    許可された形式（JPEG、PNG、WebP）のみを受け入れる。

    Args:
        content_type: リクエストのContent-Type
        file_content: 画像ファイルのバイナリデータ

    Returns:
        str: 検証済みのファイル拡張子（jpg, png, webp）

    Raises:
        ValidationError: 許可されていない画像形式の場合
    """
    # Content-Typeの検証
    if content_type not in CONTENT_TYPE_EXTENSIONS:
        raise ValidationError(
            "画像形式が不正です。JPEG、PNG、WebP形式のみ対応しています"
        )

    # マジックバイトによる実際のファイル形式検証
    if not file_content:
        raise ValidationError("画像ファイルが空です")

    is_valid = False

    # JPEG検証
    if content_type == "image/jpeg":
        for magic in IMAGE_MAGIC_BYTES["jpeg"]:
            if file_content.startswith(magic):
                is_valid = True
                break

    # PNG検証
    elif content_type == "image/png":
        for magic in IMAGE_MAGIC_BYTES["png"]:
            if file_content.startswith(magic):
                is_valid = True
                break

    # WebP検証（RIFFヘッダー + WEBPシグネチャ）
    elif content_type == "image/webp":
        if file_content[:4] == b"RIFF" and len(file_content) >= 12:
            if file_content[8:12] == b"WEBP":
                is_valid = True

    if not is_valid:
        raise ValidationError(
            "画像ファイルの内容がContent-Typeと一致しません。"
            "JPEG、PNG、WebP形式のファイルをアップロードしてください"
        )

    return CONTENT_TYPE_EXTENSIONS[content_type]


def generate_image_key(product_id: str, extension: str) -> str:
    """S3オブジェクトキーを生成する

    形式: products/{productId}/{uuid}.{ext}

    Args:
        product_id: 商品ID
        extension: ファイル拡張子（jpg, png, webp）

    Returns:
        str: S3オブジェクトキー
    """
    unique_id = str(uuid.uuid4())
    return f"products/{product_id}/{unique_id}.{extension}"


def validate_image_size(file_content: bytes) -> None:
    """画像ファイルサイズを検証する

    最大ファイルサイズ（5MB）を超える場合はエラーを発生させる。

    Args:
        file_content: 画像ファイルのバイナリデータ

    Raises:
        ValidationError: ファイルサイズが5MBを超える場合
    """
    if len(file_content) > MAX_IMAGE_SIZE:
        size_mb = len(file_content) / (1024 * 1024)
        raise ValidationError(
            f"画像ファイルサイズが上限を超えています（{size_mb:.1f}MB）。"
            f"最大5MBまでアップロード可能です"
        )
