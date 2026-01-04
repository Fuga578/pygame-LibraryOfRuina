import random
from dataclasses import dataclass
from enum import Enum
from collections import deque
from typing import Deque


class DiceType(Enum):
    EVADE = "回避"
    BLOCK = "防御"
    SLASH = "斬撃"
    PIERCE = "突き"
    BLUNT = "打撃"


EVADE_TYPES = [
    DiceType.EVADE,
]


BLOCK_TYPES = [
    DiceType.BLOCK,
]


ATTACK_TYPES = [
    DiceType.SLASH,
    DiceType.PIERCE,
    DiceType.BLUNT,
]


def is_evade(dice):
    return dice.d_type in EVADE_TYPES


def is_block(dice):
    return dice.d_type in BLOCK_TYPES


def is_attack(dice):
    return dice.d_type in ATTACK_TYPES


@dataclass
class Dice:
    min_val: int        # ダイスの最小値
    max_val: int        # ダイスの最大値
    d_type: DiceType    # ダイスの種類
    val: int | None = None     # ダイスの値

    def roll(self):
        self.val = random.randint(self.min_val, self.max_val)
        return self.val


@dataclass(eq=False)
class VelocityDice:
    min_val: int
    max_val: int
    val: int | None = None
    owner: "Unit" = None
    target: "VelocityDice" = None
    card: "Card" = None
    is_checked: bool = False
    select_order: int = 0

    def init(self):
        self.val = None
        self.target = None
        self.card = None
        self.is_checked = False
        self.select_order = 0

    def roll(self):
        self.val = random.randint(self.min_val, self.max_val)
        return self.val
