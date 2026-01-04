import pygame
from scripts.ui.battle.card import CardView


class HandView:
    def __init__(
        self,
        game,
        size: list[int, int] | tuple[int, int],
        pos: list[int, int] | tuple[int, int],
    ):
        self.game = game
        self.size = list(size)
        self.pos = list(pos)

        # 画像（代わり）
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

        # 手札のカードUI
        self.card_views = []

    def set_hand(self, cards):
        self.card_views.clear()
        card_w = 212
        pad = 8
        card_w, card_h = card_w - pad*2, 200
        gap = 8
        x = self.rect.x + pad
        y = self.rect.y + pad
        for i, c in enumerate(cards):
            r = pygame.Rect(x + i * (card_w + gap), y, card_w, card_h)
            self.card_views.append(CardView(self.game, c, (card_w, 200), (r.x, r.y)))

    def render(self, surface):
        pygame.draw.rect(surface, (240, 240, 240), self.rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=2, border_radius=10)
        for cv in self.card_views:
            cv.render(surface)

    def get_clicked_card(self, mouse_pos):
        for cv in self.card_views:
            if cv.is_hovered(mouse_pos):
                return cv.card
        return None
