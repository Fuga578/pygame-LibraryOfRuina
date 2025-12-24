from scripts.core.constants import Constants
from scripts.scene.base import Scene, SceneId
from scripts.utils.draw import draw_text, Anchor


class BattleScene(Scene):
    """
    戦闘シーン
    Args:
        game (Game): ゲームオブジェクト
        manager (SceneManager): シーンマネージャー
    """
    def __init__(self, game, manager):
        self.game = game
        self.manager = manager

        self.font = self.game.fonts.get("dot", 48)

    def handle(self):
        pass

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((50, 50, 50))
        draw_text(
            surface=surface,
            font=self.font,
            text="バトル画面",
            color=(255, 255, 255),
            pos=(Constants.SCREEN_WIDTH // 2, Constants.SCREEN_HEIGHT // 2 - 150),
            anchor=Anchor.CENTER,
        )
