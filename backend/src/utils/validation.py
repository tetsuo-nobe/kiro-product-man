"""商品データバリデーションモジュール"""


class ValidationError(Exception):
    """バリデーションエラー

    入力データが要件を満たさない場合に発生する例外。
    """

    pass


class NotFoundError(Exception):
    """リソース未検出エラー

    指定されたリソースが存在しない場合に発生する例外。
    """

    pass


def validate_product_data(data: dict) -> None:
    """商品データのバリデーションを実行する

    以下のルールを検証する:
    - 商品名称: 必須、1〜200文字
    - 価格: 必須、0以上の整数
    - 商品概要: 任意、最大2000文字

    Args:
        data: バリデーション対象の商品データ辞書

    Raises:
        ValidationError: バリデーションルールに違反した場合
    """
    errors = []

    # 商品名称のバリデーション
    product_name = data.get("productName")
    if product_name is None or product_name == "":
        errors.append("商品名称は必須です")
    elif not isinstance(product_name, str):
        errors.append("商品名称は文字列で指定してください")
    elif len(product_name.strip()) == 0:
        errors.append("商品名称は必須です")
    elif len(product_name) > 200:
        errors.append("商品名称は200文字以内で入力してください")

    # 価格のバリデーション
    price = data.get("price")
    if price is None:
        errors.append("価格は必須です")
    else:
        try:
            price_value = int(price)
            if price_value < 0:
                errors.append("価格は0以上の整数で入力してください")
        except (TypeError, ValueError):
            errors.append("価格は0以上の整数で入力してください")

    # 商品概要のバリデーション（任意項目）
    description = data.get("description")
    if description is not None:
        if not isinstance(description, str):
            errors.append("商品概要は文字列で指定してください")
        elif len(description) > 2000:
            errors.append("商品概要は2000文字以内で入力してください")

    if errors:
        raise ValidationError(errors[0])
