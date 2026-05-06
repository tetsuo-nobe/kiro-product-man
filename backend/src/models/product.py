"""商品情報モデル定義モジュール"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    """商品情報エンティティ

    DynamoDBの商品テーブルに対応するデータクラス。
    商品ID、商品名称、価格、商品概要、商品画像キー、作成日時、更新日時を保持する。
    """

    product_id: str
    product_name: str
    price: int
    description: Optional[str] = None
    image_key: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        """DynamoDB保存用辞書に変換する

        Optional項目（description, image_key）はNoneの場合に辞書から除外する。

        Returns:
            dict: DynamoDBアイテム形式の辞書
        """
        item = {
            "productId": self.product_id,
            "productName": self.product_name,
            "price": self.price,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
        if self.description is not None:
            item["description"] = self.description
        if self.image_key is not None:
            item["imageKey"] = self.image_key
        return item

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """DynamoDBアイテムからProductインスタンスを生成する

        Args:
            data: DynamoDBから取得したアイテム辞書

        Returns:
            Product: 商品情報インスタンス
        """
        return cls(
            product_id=data["productId"],
            product_name=data["productName"],
            price=int(data["price"]),
            description=data.get("description"),
            image_key=data.get("imageKey"),
            created_at=data.get("createdAt", ""),
            updated_at=data.get("updatedAt", ""),
        )
