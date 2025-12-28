from dataclasses import dataclass
from enum import Enum, auto
from scripts.models.deck import Deck
from scripts.models.card import Card
from scripts.models.dice import VelocityDice


class ResistanceType(Enum):
    VULNERABLE = 2.0    # 脆弱
    WEAK = 1.5          # 弱点
    NORMAL = 1.0        # 普通
    RESIST = 0.5        # 抵抗
    STRONG = 0.25       # 耐性
    IMMUNE = 0.0        # 免疫


@dataclass
class Unit:
    name: str       # ユニット名
    max_hp: int     # 最大HP
    max_confusion_resist: int   # 最大混乱耐性
    max_light: int  # 最大光
    min_speed: int  # 最小速度
    max_speed: int  # 最大速度
    deck: Deck      # デッキ
    is_ally: bool   # 味方判定
    hp_slash_resistance: ResistanceType = ResistanceType.NORMAL    # 斬撃耐性（体力）
    hp_pierce_resistance: ResistanceType = ResistanceType.NORMAL   # 突き耐性（体力）
    hp_blunt_resistance: ResistanceType = ResistanceType.NORMAL    # 打撃耐性（体力）
    confusion_slash_resistance: ResistanceType = ResistanceType.NORMAL   # 斬撃耐性（混乱耐性）
    confusion_pierce_resistance: ResistanceType = ResistanceType.NORMAL  # 突き耐性（混乱耐性）
    confusion_blunt_resistance: ResistanceType = ResistanceType.NORMAL   # 打撃耐性（混乱耐性）

    def __post_init__(self):
        self.hp = self.max_hp   # 現在のHP
        self.confusion_resist = self.max_confusion_resist           # 現在の混乱耐性
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

    def is_confused(self):
        return self.confusion_resist <= 0

    def can_play_card(self, card: Card) -> bool:
        return self.light >= card.cost and not self.is_confused()

    def is_dead(self):
        return self.hp <= 0

    def recover_light(self, amount: int = 1):
        self.light = min(self.max_light, self.light + amount)

    def pay_light(self, cost: int) -> bool:
        if self.light < cost:
            return False
        self.light -= cost
        return True
