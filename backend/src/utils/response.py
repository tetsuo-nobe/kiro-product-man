"""Lambda関数レスポンスヘルパーモジュール"""

import json
import logging
import traceback
from functools import wraps

from src.utils.validation import NotFoundError, ValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# CORSヘッダー（全レスポンスに付与）
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
}


def success_response(status_code: int, body: dict) -> dict:
    """成功レスポンスを生成する

    CORSヘッダーを付与した標準的なAPI Gatewayレスポンス形式を返す。

    Args:
        status_code: HTTPステータスコード
        body: レスポンスボディ（辞書）

    Returns:
        dict: API Gateway互換のレスポンス辞書
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            **CORS_HEADERS,
        },
        "body": json.dumps(body, ensure_ascii=False),
    }


def error_response(status_code: int, error_type: str, message: str) -> dict:
    """エラーレスポンスを生成する

    統一されたエラーレスポンス形式でCORSヘッダーを付与して返す。

    Args:
        status_code: HTTPステータスコード
        error_type: エラー種別（例: ValidationError, NotFoundError）
        message: エラーメッセージ

    Returns:
        dict: API Gateway互換のエラーレスポンス辞書
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            **CORS_HEADERS,
        },
        "body": json.dumps(
            {"error": error_type, "message": message}, ensure_ascii=False
        ),
    }


def handle_exceptions(func):
    """Lambda関数の共通例外ハンドリングデコレータ

    以下の例外を適切なHTTPレスポンスに変換する:
    - ValidationError → 400 Bad Request
    - NotFoundError → 404 Not Found
    - その他の例外 → 500 Internal Server Error

    Args:
        func: デコレート対象のLambdaハンドラ関数

    Returns:
        wrapper: 例外ハンドリング付きのラッパー関数
    """

    @wraps(func)
    def wrapper(event, context):
        try:
            return func(event, context)
        except ValidationError as e:
            logger.warning(f"バリデーションエラー: {e}")
            return error_response(400, "ValidationError", str(e))
        except NotFoundError as e:
            logger.warning(f"リソース未検出: {e}")
            return error_response(404, "NotFoundError", str(e))
        except Exception as e:
            logger.error(f"予期しないエラー: {e}\n{traceback.format_exc()}")
            return error_response(500, "InternalError", "内部エラーが発生しました")

    return wrapper
