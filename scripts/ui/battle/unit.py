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

        # 画像（代わり）
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

        # 速度ダイス画像（代わり）
        self.vel_dice_ui_list = [
            VelocityDiceView(
                game=game,
                velocity_dice=vel_dice,
                size=(32, 32),
                pos=(self.rect.x + 8 + i * 40, self.rect.bottom - 40)
            )
            for i, vel_dice in enumerate(self.unit.velocity_dice_list)
        ]

        # フォント
        self.font = self.game.fonts.get("dot", 20)
        self.small_font = self.game.fonts.get("dot", 12)

    def render(self, surface: pygame.Surface):
        # パネル
        pygame.draw.rect(surface, (250, 250, 250), self.rect, border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=2, border_radius=8)

        x, y = self.rect.x, self.rect.y
        pad = 8

        # 名前
        name_surf = self.font.render(self.unit.name, True, (0, 0, 0))
        surface.blit(name_surf, (x + pad, y + pad))

        # バーの共通設定
        bar_w = self.rect.w - pad * 2
        bar_h = 10

        # HPバー
        hp_y = y + pad + 50
        self._render_bar(
            surface,
            pygame.Rect(x + pad, hp_y, bar_w, bar_h),
            current=self.unit.hp,
            maximum=self.unit.max_hp,
            label=f"HP {self.unit.hp}/{self.unit.max_hp}",
        )

        # 混乱耐性バー
        st_y = hp_y + 32
        self._render_bar(
            surface,
            pygame.Rect(x + pad, st_y, bar_w, bar_h),
            current=self.unit.confusion_resist,
            maximum=self.unit.max_confusion_resist,
            label=f"ST {self.unit.confusion_resist}/{self.unit.max_confusion_resist}",
        )

        # 光（Light）
        light_y = st_y + 16
        light_text = f"Light {self.unit.light}/{self.unit.max_light}"
        light_surf = self.font.render(light_text, True, (0, 0, 0))
        surface.blit(light_surf, (x + pad, light_y))

        # 速度ダイス
        for vel_dice_ui in self.vel_dice_ui_list:
            vel_dice_ui.render(surface)

    def _render_bar(self, surface, rect, current, maximum, label: str):
        # 背景（空ゲージ）
        pygame.draw.rect(surface, (50, 50, 50), rect, border_radius=6)

        # 値が0除算にならないように
        if maximum <= 0:
            ratio = 0.0
        else:
            ratio = max(0.0, min(1.0, current / maximum))

        fill_rect = rect.copy()
        fill_rect.w = int(rect.w * ratio)
        pygame.draw.rect(surface, (140, 180, 255), fill_rect, border_radius=6)

        # ラベル（小さめに表示）
        label_surf = self.small_font.render(label, True, (0, 0, 0))
        surface.blit(label_surf, (rect.x, rect.y - 14))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def get_hovered_vel_dice_ui(self, mouse_pos):
        for vel_dice_ui in self.vel_dice_ui_list:
            if vel_dice_ui.is_hovered(mouse_pos):
                return vel_dice_ui
        return None
