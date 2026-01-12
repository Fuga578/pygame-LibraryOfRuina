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

        self.img = pygame.transform.scale(self.game.assets["battle_start_button"], size=self.size)
        self.rect = self.img.get_rect(topleft=self.pos)

    def render(self, surface):
        surface.blit(self.img, self.rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
