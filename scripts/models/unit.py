from dataclasses import dataclass
from scripts.models.deck import Deck
from scripts.models.dice import VelocityDice


@dataclass
class Unit:
    name: str       # ユニット名
    max_hp: int     # 最大HP
    max_confusion_resist: int   # 最大混乱抵抗値
    max_light: int  # 最大光
    min_speed: int  # 最小速度
    max_speed: int  # 最大速度
    deck: Deck      # デッキ
    is_ally: bool   # 味方判定

    def __post_init__(self):
        self.hp = self.max_hp   # 現在のHP
        self.confusion_resist = self.max_confusion_resist           # 現在の混乱抵抗値
        self.light = self.max_light     # 現在の光
        self.velocity_dice_list = self._create_velocity_dice(1)     # 速度ダイスリスト

    def _create_velocity_dice(self, n):
        velocity_dice_list = [
            VelocityDice(
                min_val=self.min_speed,
                max_val=self.max_speed,
                owner=self,
            )
            for _ in range(n)
        ]
        return velocity_dice_list
