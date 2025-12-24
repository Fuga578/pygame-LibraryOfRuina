from dataclasses import dataclass
from scripts.models.dice import Dice


@dataclass
class Card:
    name: str   # カード名
    cost: int   # コスト
    dice_list: list[Dice]   # ダイスリスト（回避や斬撃）
