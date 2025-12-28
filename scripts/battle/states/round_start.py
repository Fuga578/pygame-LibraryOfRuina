from scripts.battle.states.base import BattleState


class RoundStartState(BattleState):
    """
    ラウンド開始ステート

    ・ユニットがカードをドロー
    ・ユニットの速度ダイスを振る
    """

    def enter(self) -> None:
        print("Enter: RoundStartState")
        self.scene.state_name = "ROUND START STATE"

    def exit(self) -> None:
        print("Exit: RoundStartState")

    def handle(self) -> None:
        if self.scene.game.inputs["left_click_down"]:

            # ラウンド開始処理
            units = self.scene.allies + self.scene.enemies
            self.scene.system.start_round(units)

            # 全体の速度順（速度ダイス）決定
            self.scene.all_slots = self.scene.system.get_action_order(units)

            # 味方の速度順（速度ダイス）決定
            self.scene.ally_slots = [
                v for v in self.scene.all_slots if v.owner.is_ally
            ]

            # 敵の速度順（速度ダイス）決定
            self.scene.enemy_slots = [
                v for v in self.scene.all_slots if not v.owner.is_ally
            ]

            # 次の状態へ遷移
            self._go_next_state()

    def update(self, dt: float) -> None:
        pass

    def render(self, surface) -> None:
        pass

    def _go_next_state(self):
        # 次の状態へ遷移
        from scripts.battle.states.enemy_plan import EnemyPlanState
        self.scene.change_state(EnemyPlanState(self.scene))
