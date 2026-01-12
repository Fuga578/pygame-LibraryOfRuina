import random
from scripts.battle.states.base import BattleState


class EnemyPlanState(BattleState):
    """
    敵の戦闘準備ステート

    ・敵が速度ダイスにカードをセットし、ターゲットを選択
    """

    def enter(self) -> None:
        print("Enter: EnemyPlanState")
        self.scene.state_name = "ENEMY PLAN STATE"

        # 敵の準備処理を実行
        self.scene.system.plan_enemy(
            enemy_slots=self.scene.enemy_slots,
            ally_slots=self.scene.ally_slots,
        )

        # 次の状態へ遷移
        self._go_next_state()

    def exit(self) -> None:
        print("Exit: EnemyPlanState")

    def handle(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface) -> None:
        pass

    def _go_next_state(self):
        # 次の状態へ遷移
        from scripts.battle.states.ally_plan import AllyPlanState
        self.scene.change_state(AllyPlanState(self.scene))
