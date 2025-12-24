from dataclasses import dataclass
from scripts.models.card import Card


@dataclass
class Deck:
    card_list: list[Card]    # カードリスト

    def __post_init__(self):
        self.draw_pile = self.card_list.copy()  # 山札
        self.hand_card = []
