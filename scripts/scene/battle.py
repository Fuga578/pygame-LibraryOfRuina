from scripts.scene.base import Scene
from scripts.utils.draw import draw_text, Anchor
from scripts.battle.states.battle_start import BattleStartState
from scripts.battle.context import BattleContext
from scripts.battle.system import BattleSystem


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

        self.allies = []    # 味方ユニット一覧
        self.enemies = []   # 敵ユニット一覧
        self.ally_slots = []    # 味方の速度ダイス一覧（速度順）
        self.enemy_slots = []   # 敵の速度ダイス一覧（速度順）
        self.all_slots = []     # 全ユニットの速度ダイス一覧（速度順）

        # コンテキスト
        self.context = BattleContext()

        # システム
        self.system = BattleSystem()

        # 状態
        self.state_name = ""
        self.state = BattleStartState(self)
        self.state.enter()

        self.font = self.game.fonts.get("dot", 20)

    def handle(self):
        self.state.handle()

    def update(self, dt):
        self.state.update(dt)

    def render(self, surface):
        surface.fill((255, 255, 255))
        draw_text(
            surface=surface,
            font=self.font,
            text=self.state_name,
            color=(30, 30, 30),
            pos=(20, 20)
        )
        self.state.render(surface)

    def change_state(self, next_state):
        """状態を変更する"""
        if self.state:
            self.state.exit()
        self.state = next_state
        self.state.enter()
