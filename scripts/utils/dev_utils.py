from scripts.models.dice import Dice, DiceType
from scripts.models.card import Card


def create_sample_cards() -> list[Card]:
    """サンプルカードを作成する"""
    card_list = []

    card1 = Card(
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
        name="1回避",
        cost=0,
        dice_list=[
            Dice(min_val=1, max_val=6, d_type=DiceType.EVADE),
        ],
    )
    card_list.append(card6)

    card7 = Card(
        name="1防御",
        cost=1,
        dice_list=[
            Dice(min_val=1, max_val=6, d_type=DiceType.BLOCK),
        ],
    )
    card_list.append(card7)

    card8 = Card(
        name="1斬撃",
        cost=1,
        dice_list=[
            Dice(min_val=1, max_val=6, d_type=DiceType.SLASH),
        ],
    )
    card_list.append(card8)

    card9 = Card(
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
