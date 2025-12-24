from dataclasses import dataclass
from enum import Enum
from scripts.models.card import Card


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


@dataclass
class VelocityDice:
    min_val: int
    max_val: int
    val: int | None = None
    owner: "Unit" = None
    target: "VelocityDice" = None
    card: Card = None
