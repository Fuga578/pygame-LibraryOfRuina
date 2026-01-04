import pygame
from scripts.scene.base import Scene
from scripts.utils.draw import draw_text, Anchor
from scripts.battle.states.battle_start import BattleStartState
from scripts.battle.context import BattleContext
from scripts.battle.system import BattleSystem
from scripts.ui.battle.unit import UnitView
from scripts.ui.battle.battle_start_button import BattleStartButton


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

        # マッチ/一方攻撃の情報
        self.clash_infos = self.system.evaluate_clashes(self.all_slots)

        # 状態
        self.state_name = ""
        self.state = BattleStartState(self)
        self.state.enter()

        # フォント
        self.font = self.game.fonts.get("dot", 20)

        # ユニットのUI
        self.allies_ui = []
        self.enemies_ui = []

        # バトル開始ボタン
        self.battle_start_button = BattleStartButton(self.game, size=(80, 50), pos=(self.game.screen.get_width() // 2 - 80/2, 10))

    def handle(self):
        self.state.handle()

    def update(self, dt):
        # 味方UI更新
        for ally_ui in self.allies_ui:
            ally_ui.update(dt)

        # 敵UI更新
        for enemy_ui in self.enemies_ui:
            enemy_ui.update(dt)

        self.state.update(dt)

    def render(self, surface):
        surface.fill((200, 200, 200))

        # 現在の状態表示
        draw_text(
            surface=surface,
            font=self.font,
            text=self.state_name,
            color=(30, 30, 30),
            pos=(20, 20)
        )

        # 味方UI表示
        for ally_ui in self.allies_ui:
            ally_ui.render(surface)

        # 敵UI表示
        for enemy_ui in self.enemies_ui:
            enemy_ui.render(surface)

        self.battle_start_button.render(surface)

        # 各状態ごとの表示
        self.state.render(surface)

    def change_state(self, next_state):
        """状態を変更する"""
        if self.state:
            self.state.exit()
        self.state = next_state
        self.state.enter()

    def _create_unit_panels(self):

        self.allies_ui.clear()
        self.enemies_ui.clear()

        w, h = 128, 128

        # 左：敵
        enemy_pos_list = [(200, 250), (350, 100), (350, 400), (50, 100), (50, 400)]
        for i, unit in enumerate(self.enemies):
            self.enemies_ui.append(
                UnitView(
                    game=self.game,
                    unit=unit,
                    size=(w, h),
                    pos=enemy_pos_list[i]
                ),
            )

        # 右：味方
        screen_w = self.game.screen.get_width()
        ally_pos_list = [(screen_w - 200 - w, 250), (screen_w - 350 - w, 100), (screen_w - 350 - w, 400), (screen_w - 50 - w, 100), (screen_w - 50 - w, 400)]
        for i, unit in enumerate(self.allies):
            self.allies_ui.append(UnitView(
                game=self.game,
                unit=unit,
                size=(w, h),
                pos=ally_pos_list[i]
            ))
