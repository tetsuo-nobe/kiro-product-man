"""画像処理ユーティリティの単体テスト"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest
from src.utils.image import (
    validate_image_format,
    generate_image_key,
    validate_image_size,
    MAX_IMAGE_SIZE,
)
from src.utils.validation import ValidationError


# テスト用マジックバイト
JPEG_MAGIC = b"\xff\xd8\xff\xe0" + b"\x00" * 100
PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
WEBP_MAGIC = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP" + b"\x00" * 100
INVALID_MAGIC = b"\x00\x01\x02\x03" + b"\x00" * 100


def test_validate_jpeg_format():
    """JPEG形式の画像がバリデーションを通過すること"""
    ext = validate_image_format("image/jpeg", JPEG_MAGIC)
    assert ext == "jpg"


def test_validate_png_format():
    """PNG形式の画像がバリデーションを通過すること"""
    ext = validate_image_format("image/png", PNG_MAGIC)
    assert ext == "png"


def test_validate_webp_format():
    """WebP形式の画像がバリデーションを通過すること"""
    ext = validate_image_format("image/webp", WEBP_MAGIC)
    assert ext == "webp"


def test_invalid_content_type():
    """許可されていないContent-Typeが拒否されること"""
    with pytest.raises(ValidationError, match="画像形式が不正です"):
        validate_image_format("image/gif", b"\x47\x49\x46\x38" + b"\x00" * 100)


def test_mismatched_content_type_and_magic():
    """Content-Typeとマジックバイトが一致しない場合に拒否されること"""
    with pytest.raises(ValidationError, match="一致しません"):
        validate_image_format("image/jpeg", PNG_MAGIC)


def test_empty_file_content():
    """空のファイルが拒否されること"""
    with pytest.raises(ValidationError, match="画像ファイルが空です"):
        validate_image_format("image/jpeg", b"")


def test_generate_image_key_format():
    """生成されるS3キーが正しい形式であること"""
    key = generate_image_key("prod-123", "jpg")
    assert key.startswith("products/prod-123/")
    assert key.endswith(".jpg")


def test_generate_image_key_uniqueness():
    """生成されるS3キーが毎回異なること"""
    key1 = generate_image_key("prod-123", "jpg")
    key2 = generate_image_key("prod-123", "jpg")
    assert key1 != key2


def test_validate_image_size_within_limit():
    """5MB以内のファイルがバリデーションを通過すること"""
    content = b"\x00" * (MAX_IMAGE_SIZE - 1)
    validate_image_size(content)  # 例外が発生しないこと


def test_validate_image_size_exceeds_limit():
    """5MBを超えるファイルが拒否されること"""
    content = b"\x00" * (MAX_IMAGE_SIZE + 1)
    with pytest.raises(ValidationError, match="上限を超えています"):
        validate_image_size(content)


def test_validate_image_size_exact_limit():
    """ちょうど5MBのファイルがバリデーションを通過すること"""
    content = b"\x00" * MAX_IMAGE_SIZE
    validate_image_size(content)  # 例外が発生しないこと
