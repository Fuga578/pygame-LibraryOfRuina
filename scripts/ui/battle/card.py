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
        name_surf = self.font.render(self.card.name, True, (0, 0, 0))
        surface.blit(name_surf, (self.rect.x + 50, self.rect.y + 13))

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
