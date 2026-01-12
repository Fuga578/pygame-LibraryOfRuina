import pygame
from scripts.models.unit import Unit, DamageType, HealType
from scripts.ui.battle.velocity_dice import VelocityDiceView


class DamagePopup:
    def __init__(self, amount: int, damage_type: DamageType, ttl: float = 0.6):
        self.amount = amount
        self.damage_type = damage_type
        self.ttl = ttl

        self.age = 0.0
        self.y_offset = 0.0

    def update(self, dt: float):
        self.age += dt
        self.y_offset -= 30 * dt  # 上に移動

    @property
    def alive(self) -> bool:
        return self.age < self.ttl


class HealPopup:
    def __init__(self, amount: int, heal_type: HealType, ttl: float = 0.6):
        self.amount = amount
        self.heal_type = heal_type
        self.ttl = ttl

        self.age = 0.0
        self.y_offset = 0.0

    def update(self, dt: float):
        self.age += dt
        self.y_offset -= 30 * dt  # 上に移動

    @property
    def alive(self) -> bool:
        return self.age < self.ttl


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

        # 半透明
        self.is_dimmed = False
        self.alpha = 100

        # ダメージUI
        self.hit_flash = 0.0
        self.popups_damage: list[DamagePopup] = []

        # 回復UI
        self.popups_heal: list[HealPopup] = []

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
        self.font = self.game.fonts.get("dot", 35)
        self.small_font = self.game.fonts.get("dot", 12)

    def on_damage(self, amount: int, damage_type: DamageType = DamageType.HP):
        if amount <= 0:
            return
        self.hit_flash = 0.15
        self.popups_damage.append(DamagePopup(amount, damage_type))

    def on_heal(self, amount: int, heal_type: HealType = HealType.HP):
        if amount <= 0:
            return
        self.popups_heal.append(HealPopup(amount, heal_type))

    def update(self, dt: float):
        self.animation.update(dt)
        self.img = pygame.transform.scale(self.animation.get_img(), size=self.size)

        # ダメージ判定
        if self.hit_flash > 0:
            self.hit_flash = max(0.0, self.hit_flash - dt)
        for p in self.popups_damage:
            p.update(dt)
        self.popups_damage = [p for p in self.popups_damage if p.alive]

        # 回復判定
        for p in self.popups_heal:
            p.update(dt)
        self.popups_heal = [p for p in self.popups_heal if p.alive]

    def render(self, surface: pygame.Surface):
        ui_surf = pygame.Surface(surface.size, pygame.SRCALPHA)

        img = self.img
        img.set_alpha(255)
        if self.is_dimmed:
            img.set_alpha(self.alpha)
        surface.blit(img, self.rect)

        # HPバー
        self._render_bar(
            ui_surf,
            pygame.Rect(self.rect.left, self.rect.bottom, self.rect.width, 5),
            current=self.unit.hp,
            maximum=self.unit.max_hp,
            color=(255, 0, 0, self.alpha) if self.is_dimmed else (255, 0, 0),
            label=f"{self.unit.hp}/{self.unit.max_hp}",
        )

        # 混乱耐性バー
        self._render_bar(
            ui_surf,
            pygame.Rect(self.rect.left, self.rect.bottom + 15, self.rect.width, 5),
            current=self.unit.confusion_resist,
            maximum=self.unit.max_confusion_resist,
            color=(255, 255, 0, self.alpha) if self.is_dimmed else (255, 255, 0),
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
                color = (255, 255, 0, self.alpha) if self.is_dimmed else (255, 255, 0)
            else:
                color = (255, 255, 100, self.alpha) if self.is_dimmed else (255, 255, 100)

            pygame.draw.circle(surface, color, (x, y), 3)

        # 速度ダイス
        for vel_dice_ui in self.vel_dice_ui_list:
            vel_dice_ui.render(surface)

        # ダメージフラッシュ
        if self.hit_flash > 0:
            overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 140))
            surface.blit(overlay, self.rect.topleft)

        # ダメージ数字ポップ
        for p in self.popups_damage:
            text = f"-{p.amount}"
            # HPダメージの場合
            if p.damage_type == DamageType.HP:
                surf = self.font.render(text, True, (255, 0, 0))
                x = self.rect.centerx - surf.get_width() // 2 - 20
                y = self.rect.top - 20 + int(p.y_offset)
            # 混乱ダメージの場合
            else:
                surf = self.font.render(text, True, (255, 255, 0))
                x = self.rect.centerx - surf.get_width() // 2 + 20
                y = self.rect.top - 20 + int(p.y_offset)

            surface.blit(surf, (x, y))

        # 回復数字ポップ
        for p in self.popups_heal:
            text = f"+{p.amount}"
            surf = self.font.render(text, True, (0, 255, 255))
            # HPダメージの場合
            if p.heal_type == DamageType.HP:
                x = self.rect.centerx - surf.get_width() // 2 - 20
                y = self.rect.top - 20 + int(p.y_offset)
            # 混乱ダメージの場合
            else:
                x = self.rect.centerx - surf.get_width() // 2 + 20
                y = self.rect.top - 20 + int(p.y_offset)

            surface.blit(surf, (x, y))

        surface.blit(ui_surf, (0, 0))

    def _render_bar(self, surface, rect, current, maximum, color, label: str):
        # 背景（空ゲージ）
        if self.is_dimmed:
            pygame.draw.rect(surface, (50, 50, 50), rect, border_radius=6)
        else:
            pygame.draw.rect(surface, (50, 50, 50, self.alpha), rect, border_radius=6)

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
