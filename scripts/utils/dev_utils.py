from scripts.models.dice import Dice, DiceType
from scripts.models.card import Card
from scripts.models.unit import Unit
from copy import deepcopy


def create_sample_cards() -> list[Card]:
    """サンプルカードを作成する"""
    card_list = []

    card1 = Card(
        id="three_slash",
        name="3斬撃",
        cost=2,
        dice_list=[
            Dice(min_val=1, max_val=4, d_type=DiceType.SLASH),
            Dice(min_val=2, max_val=5, d_type=DiceType.SLASH),
            Dice(min_val=3, max_val=6, d_type=DiceType.SLASH),
        ],
    )
    card_list.append(card1)

    card2 = Card(
        id="three_pierce",
        name="3突き",
        cost=2,
        dice_list=[
            Dice(min_val=1, max_val=4, d_type=DiceType.PIERCE),
            Dice(min_val=2, max_val=5, d_type=DiceType.PIERCE),
            Dice(min_val=3, max_val=6, d_type=DiceType.PIERCE),
        ],
    )
    card_list.append(card2)

    card3 = Card(
        id="three_blunt",
        name="3打撃",
        cost=2,
        dice_list=[
            Dice(min_val=1, max_val=4, d_type=DiceType.BLUNT),
            Dice(min_val=2, max_val=5, d_type=DiceType.BLUNT),
            Dice(min_val=3, max_val=6, d_type=DiceType.BLUNT),
        ],
    )
    card_list.append(card3)

    card4 = Card(
        id="three_evade",
        name="3回避",
        cost=2,
        dice_list=[
            Dice(min_val=1, max_val=4, d_type=DiceType.EVADE),
            Dice(min_val=2, max_val=5, d_type=DiceType.EVADE),
            Dice(min_val=3, max_val=6, d_type=DiceType.EVADE),
        ],
    )
    card_list.append(card4)

    card5 = Card(
        id="three_block",
        name="3防御",
        cost=2,
        dice_list=[
            Dice(min_val=1, max_val=4, d_type=DiceType.BLOCK),
            Dice(min_val=2, max_val=5, d_type=DiceType.BLOCK),
            Dice(min_val=3, max_val=6, d_type=DiceType.BLOCK),
        ],
    )
    card_list.append(card5)

    card6 = Card(
        id="one_evade",
        name="1回避",
        cost=0,
        dice_list=[
            Dice(min_val=1, max_val=6, d_type=DiceType.EVADE),
        ],
    )
    card_list.append(card6)

    card7 = Card(
        id="one_block",
        name="1防御",
        cost=1,
        dice_list=[
            Dice(min_val=1, max_val=6, d_type=DiceType.BLOCK),
        ],
    )
    card_list.append(card7)

    card8 = Card(
        id="one_slash",
        name="1斬撃",
        cost=1,
        dice_list=[
            Dice(min_val=1, max_val=6, d_type=DiceType.SLASH),
        ],
    )
    card_list.append(card8)

    card9 = Card(
        id="one_evade_block_slash",
        name="1回避 1防御 1斬撃",
        cost=1,
        dice_list=[
            Dice(min_val=1, max_val=4, d_type=DiceType.EVADE),
            Dice(min_val=2, max_val=5, d_type=DiceType.BLOCK),
            Dice(min_val=3, max_val=6, d_type=DiceType.SLASH),
        ],
    )
    card_list.append(card9)

    return card_list


def create_sample_units(deck, num=3, is_ally=True):

    unit_list = []

    name_prefix = "ally" if is_ally else "enemy"
    for i in range(num):
        unit = Unit(
            name=f"{name_prefix}/{i + 1}",
            max_hp=30,
            max_confusion_resist=20,
            max_light=3,
            min_speed=1,
            max_speed=6,
            deck=deepcopy(deck),
            is_ally=is_ally,
        )
        unit_list.append(unit)

    return unit_list