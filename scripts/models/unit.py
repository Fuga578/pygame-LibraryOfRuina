from dataclasses import dataclass
from enum import Enum, auto
from scripts.models.deck import Deck
from scripts.models.card import Card
from scripts.models.dice import VelocityDice, DiceType


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
        # HPの耐性
        self.hp_resistance = {
            DiceType.SLASH.name: self.hp_slash_resistance.value,
            DiceType.PIERCE.name: self.hp_pierce_resistance.value,
            DiceType.BLUNT.name: self.hp_blunt_resistance.value,
        }
        # 混乱耐性
        self.confusion_resistance = {
            DiceType.SLASH.name: self.confusion_slash_resistance.value,
            DiceType.PIERCE.name: self.confusion_pierce_resistance.value,
            DiceType.BLUNT.name: self.confusion_blunt_resistance.value,
        }
        self.remaining_dices = []   # 保存ダイス

    def init(self):
        self.remaining_dices = []
        for vel_dice in self.velocity_dice_list:
            vel_dice.init()

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

    def take_damage(self, damage, dice_type: DiceType) -> None:
        self.take_hp_damage(damage, dice_type)
        self.take_confusion_resist_damage(damage, dice_type)

    def take_hp_damage(self, damage: int, dice_type: DiceType) -> None:
        """HPダメージを受ける"""
        resistance = self.hp_resistance.get(dice_type.name)
        if resistance is None:
            resistance = 1.0
        dmg = int(damage * resistance)
        self.hp = max(0, self.hp - dmg)

    def take_confusion_resist_damage(self, damage: int, dice_type: DiceType) -> None:
        """混乱抵抗値ダメージを受ける"""
        resistance = self.confusion_resistance.get(dice_type.name)
        if resistance is None:
            resistance = 1.0
        dmg = int(damage * resistance)
        self.confusion_resist = max(0, self.confusion_resist - dmg)

    def heal_hp(self, amount: int) -> None:
        """HPを回復する"""
        self.hp = min(self.max_hp, self.hp + amount)

    def heal_confusion_resist(self, amount: int) -> None:
        """混乱抵抗値を回復する"""
        self.confusion_resist = min(self.max_confusion_resist, self.confusion_resist + amount)
