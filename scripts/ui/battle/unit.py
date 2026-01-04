import pygame
from scripts.models.unit import Unit
from scripts.ui.battle.velocity_dice import VelocityDiceView


class UnitView:
    def __init__(
        self,
        game: "Game",
        unit: Unit,
        size: list[int, int] | tuple[int, int],
        pos: list[int, int] | tuple[int, int],
    ):
        self.game = game
        self.unit = unit
        self.size = list(size)
        self.pos = list(pos)

        # 画像
        self.animation = self.game.assets.get(f"{self.unit.name}/{self.unit.states.value}")
        self.img = pygame.transform.scale(self.animation.get_img(), size=self.size)
        self.rect = self.img.get_rect(topleft=self.pos)

        # 速度ダイス画像
        self.vel_dice_ui_list = [
            VelocityDiceView(
                game=game,
                velocity_dice=vel_dice,
                size=(32, 32),
                pos=(self.rect.centerx - i * 32, self.rect.top - 8)
            )
            for i, vel_dice in enumerate(self.unit.velocity_dice_list)
        ]

        # フォント
        self.font = self.game.fonts.get("dot", 20)
        self.small_font = self.game.fonts.get("dot", 12)

    def update(self, dt: float):
        self.animation.update(dt)
        self.img = pygame.transform.scale(self.animation.get_img(), size=self.size)

    def render(self, surface: pygame.Surface):
        surface.blit(self.img, self.rect)

        # HPバー
        self._render_bar(
            surface,
            pygame.Rect(self.rect.left, self.rect.bottom, self.rect.width, 5),
            current=self.unit.hp,
            maximum=self.unit.max_hp,
            color=(255, 0, 0),
            label=f"{self.unit.hp}/{self.unit.max_hp}",
        )

        # 混乱耐性バー
        self._render_bar(
            surface,
            pygame.Rect(self.rect.left, self.rect.bottom + 15, self.rect.width, 5),
            current=self.unit.confusion_resist,
            maximum=self.unit.max_confusion_resist,
            color=(255, 255, 0),
            label=f"{self.unit.confusion_resist}/{self.unit.max_confusion_resist}",
        )

        # 光（Light）
        gap = 10
        n = self.unit.max_light
        cx = self.rect.centerx
        y = self.rect.y - 32

        # 全体の左端（中心合わせ）
        start_x = cx - (n - 1) * gap / 2

        for i in range(n):
            x = int(round(start_x + i * gap))

            if i >= self.unit.light:
                color = (255, 255, 0)  # 点灯
            else:
                color = (255, 255, 100)  # 空

            pygame.draw.circle(surface, color, (x, y), 3)

        # 速度ダイス
        for vel_dice_ui in self.vel_dice_ui_list:
            vel_dice_ui.render(surface)

    def _render_bar(self, surface, rect, current, maximum, color, label: str):
        # 背景（空ゲージ）
        pygame.draw.rect(surface, (50, 50, 50), rect, border_radius=6)

        # 値が0除算にならないように
        if maximum <= 0:
            ratio = 0.0
        else:
            ratio = max(0.0, min(1.0, current / maximum))

        fill_rect = rect.copy()
        fill_rect.w = int(rect.w * ratio)
        pygame.draw.rect(surface, color, fill_rect, border_radius=6)

        # ラベル（小さめに表示）
        label_surf = self.small_font.render(label, True, (0, 0, 0))
        surface.blit(label_surf, (rect.right, rect.y - 3))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def get_hovered_vel_dice_ui(self, mouse_pos):
        for vel_dice_ui in self.vel_dice_ui_list:
            if vel_dice_ui.is_hovered(mouse_pos):
                return vel_dice_ui
        return None
