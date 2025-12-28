import random
from dataclasses import dataclass
from enum import Enum


class DiceType(Enum):
    EVADE = "回避"
    BLOCK = "防御"
    SLASH = "斬撃"
    PIERCE = "突き"
    BLUNT = "打撃"

@dataclass
class Dice:
    min_val: int        # ダイスの最小値
    max_val: int        # ダイスの最大値
    d_type: DiceType    # ダイスの種類
    val: int | None = None     # ダイスの値

    def roll(self):
        self.val = random.randint(self.min_val, self.max_val)


@dataclass
class VelocityDice:
    min_val: int
    max_val: int
    val: int | None = None
    owner: "Unit" = None
    target: "VelocityDice" = None
    card: "Card" = None
    is_checked: bool = False

    def init(self):
        self.val = None
        self.target = None
        self.card = None
        self.is_checked = False

    def roll(self):
        self.val = random.randint(self.min_val, self.max_val)
