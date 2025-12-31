import pygame
from scripts.models.card import Card


class CardView:

    def __init__(
        self,
        game: "Game",
        card: Card,
        size: list[int, int] | tuple[int, int],
        pos: list[int, int] | tuple[int, int],
    ):
        self.game = game
        self.card = card
        self.size = list(size)
        self.pos = list(pos)

        # 画像（代わり）
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

        # フォント
        self.font = self.game.fonts.get("dot", 20)

    def render(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=6)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=2, border_radius=6)

        pad = 6
        x, y = self.rect.x + pad, self.rect.y + pad

        # カード名
        card_name_text = self.card.name
        card_name_surf = self.font.render(card_name_text, True, (0, 0, 0))
        surface.blit(card_name_surf, (x, y))

        # コスト
        cost_text = f"コスト: {self.card.cost}"
        cost_surf = self.font.render(cost_text, True, (0, 0, 0))
        surface.blit(cost_surf, (self.rect.right - pad - cost_surf.get_width(), y))

        # ダイスの内容
        dy = y + 50
        for d in self.card.dice_list:
            line = f"{d.d_type.value}: {d.min_val}-{d.max_val}"
            s = self.font.render(line, True, (0, 0, 0))
            surface.blit(s, (x, dy))
            dy += 30

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
