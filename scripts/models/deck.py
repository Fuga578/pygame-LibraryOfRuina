import random
from dataclasses import dataclass
from scripts.models.card import Card


@dataclass
class Deck:
    card_list: list[Card]    # カードリスト

    def __post_init__(self):
        self.draw_pile = self.card_list.copy()  # 山札
        self.hand_cards = []
        self.hand_limit = 9

    def shuffle_draw_pile(self):
        """山札をシャッフル"""
        random.shuffle(self.draw_pile)

    def remove_card(self, card: Card):
        self.hand_cards.remove(card)

    def draw(self, num: int):
        """カードを山札から引く"""
        for _ in range(num):

            # 山札が空の場合、補充してシャッフル
            if len(self.draw_pile) <= 0:
                self.draw_pile = self.card_list.copy()
                self.shuffle_draw_pile()

            draw_card = self.draw_pile.pop()

            # 手札が上限に達していない場合、手札に加える
            if len(self.hand_cards) < self.hand_limit:
                self.hand_cards.append(draw_card)
