import pygame


class BattleStartButton:

    def __init__(
        self,
        game: "Game",
        size: list[int, int] | tuple[int, int],
        pos: list[int, int] | tuple[int, int],
    ):
        self.game = game
        self.size = list(size)
        self.pos = list(pos)

        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def render(self, surface):
        pygame.draw.rect(surface, (100, 100, 100), self.rect, border_radius=6)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=2, border_radius=6)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
