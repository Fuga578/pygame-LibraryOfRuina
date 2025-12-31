import pygame
from scripts.models.dice import VelocityDice


class VelocityDiceView:
    def __init__(
            self,
            game: "Game",
            velocity_dice: VelocityDice,
            size: list[int, int] | tuple[int, int],
            pos: list[int, int] | tuple[int, int],
    ):
        self.game = game
        self.velocity_dice = velocity_dice
        self.size = list(size)
        self.pos = list(pos)

        # 画像（代わり）
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

        # フォント
        self.font = self.game.fonts.get("dot", 16)

    def render(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=6)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=2, border_radius=6)

        text = "-" if self.velocity_dice.val is None else str(self.velocity_dice.val)
        surf = self.font.render(text, True, (0, 0, 0))
        surface.blit(surf, (self.rect.centerx - surf.get_width() // 2,
                            self.rect.centery - surf.get_height() // 2))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
