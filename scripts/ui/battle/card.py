from scripts.models.card import Card
from scripts.models.dice import DiceType


class CardView:

    def __init__(
        self,
        game: "Game",
        card: Card,
        pos: list[int, int] | tuple[int, int],
    ):
        self.game = game
        self.card = card
        self.pos = list(pos)

        # 画像
        self.img = self.game.card_art_manager.get(id=self.card.id, scale=2.0)
        self.rect = self.img.get_rect(topleft=self.pos)

        # フォント
        self.font = self.game.fonts.get("dot", 20)

    def render(self, surface):
        # カード
        surface.blit(self.img, self.rect)

        # カード名
        name_x = self.rect.x + 50
        name_y = self.rect.y + 13
        max_width = self.rect.right - name_x - 10  # 右に余白10

        font, name_surf = self._fit_text(self.card.name, max_width, base_size=20, min_size=12)
        surface.blit(name_surf, (name_x, name_y))

        # コスト
        cost_surf = self.font.render(f"{self.card.cost}", True, (0, 0, 0))
        surface.blit(cost_surf, (self.rect.x + 19, self.rect.y + 13))

        # ダイスの内容
        for i, die in enumerate(self.card.dice_list):
            icon = None
            match die.d_type:
                # 斬撃ダイス
                case DiceType.SLASH:
                    icon = self.game.assets["slash_icon"]
                # 突きダイス
                case DiceType.PIERCE:
                    icon = self.game.assets["pierce_icon"]
                # 打撃ダイス
                case DiceType.BLUNT:
                    icon = self.game.assets["blunt_icon"]
                # 防御ダイス
                case DiceType.BLOCK:
                    icon = self.game.assets["block_icon"]
                # 回避ダイス
                case DiceType.EVADE:
                    icon = self.game.assets["evade_icon"]

            # アイコン画像
            if icon:
                surface.blit(icon, (self.rect.x + 10, self.rect.y + 155 + i * 30))

            # ダイスの値の範囲
            dice_val_surf = self.font.render(f"{die.min_val} - {die.max_val}", True, (0, 0, 0))
            surface.blit(dice_val_surf, (self.rect.x + 50, self.rect.y + 160 + i * 30))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def _fit_text(self, text: str, max_width: int, base_size: int = 20, min_size: int = 12):
        """
        1) base_size から min_size まで縮小して幅に収まるか試す
        2) それでも無理なら min_size のまま末尾を '…' で省略
        戻り値: (font, rendered_surface)
        """
        # 縮小
        for size in range(base_size, min_size - 1, -1):
            font = self.game.fonts.get("dot", size)
            if font.size(text)[0] <= max_width:
                return font, font.render(text, True, (0, 0, 0))

        # 省略
        font = self.game.fonts.get("dot", min_size)
        ell = "…"
        if font.size(text)[0] <= max_width:
            return font, font.render(text, True, (0, 0, 0))

        s = text
        while s and font.size(s + ell)[0] > max_width:
            s = s[:-1]
        return font, font.render(s + ell if s else ell, True, (0, 0, 0))
