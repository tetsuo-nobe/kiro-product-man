"""レスポンスヘルパーの単体テスト"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest
from src.utils.response import success_response, error_response, handle_exceptions
from src.utils.validation import ValidationError, NotFoundError


def test_success_response():
    """成功レスポンスが正しい形式で生成されること"""
    result = success_response(200, {"message": "成功"})
    assert result["statusCode"] == 200
    assert "Access-Control-Allow-Origin" in result["headers"]
    body = json.loads(result["body"])
    assert body["message"] == "成功"


def test_success_response_201():
    """201ステータスの成功レスポンスが生成できること"""
    result = success_response(201, {"product": {"productId": "prod-123"}})
    assert result["statusCode"] == 201


def test_error_response():
    """エラーレスポンスが正しい形式で生成されること"""
    result = error_response(400, "ValidationError", "商品名称は必須です")
    assert result["statusCode"] == 400
    assert "Access-Control-Allow-Origin" in result["headers"]
    body = json.loads(result["body"])
    assert body["error"] == "ValidationError"
    assert body["message"] == "商品名称は必須です"


def test_handle_exceptions_validation_error():
    """ValidationErrorが400レスポンスに変換されること"""

    @handle_exceptions
    def handler(event, context):
        raise ValidationError("テストエラー")

    result = handler({}, None)
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert body["error"] == "ValidationError"


def test_handle_exceptions_not_found_error():
    """NotFoundErrorが404レスポンスに変換されること"""

    @handle_exceptions
    def handler(event, context):
        raise NotFoundError("商品が見つかりません")

    result = handler({}, None)
    assert result["statusCode"] == 404
    body = json.loads(result["body"])
    assert body["error"] == "NotFoundError"


def test_handle_exceptions_unexpected_error():
    """予期しない例外が500レスポンスに変換されること"""

    @handle_exceptions
    def handler(event, context):
        raise RuntimeError("予期しないエラー")

    result = handler({}, None)
    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert body["error"] == "InternalError"
    assert body["message"] == "内部エラーが発生しました"


def test_handle_exceptions_success():
    """正常時はハンドラの戻り値がそのまま返されること"""

    @handle_exceptions
    def handler(event, context):
        return success_response(200, {"data": "test"})

    result = handler({}, None)
    assert result["statusCode"] == 200
