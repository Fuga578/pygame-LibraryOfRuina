from scripts.battle.states.base import BattleState


class ResolveState(BattleState):
    """
    戦闘処理ステート

    ・一方攻撃、マッチ判定
    """

    def enter(self) -> None:
        print("Enter: ResolveState")
        self.scene.state_name = "RESOLVE STATE"

        # 一方攻撃/マッチの判定更新
        self.scene.clash_infos = self.scene.system.evaluate_clashes(self.scene.all_slots)

    def exit(self) -> None:
        print("Exit: ResolveState")

    def handle(self) -> None:
        if self.scene.game.inputs["left_click_down"]:

            # 戦闘計算処理を実行
            self.scene.system.resolve_attack(
                self.scene.all_slots,
                self.scene.clash_infos,
            )

            # 次の状態へ遷移
            self._go_next_state()

    def update(self, dt: float) -> None:
        pass

    def render(self, surface) -> None:
        pass

    def _go_next_state(self):
        # 次の状態へ遷移
        from scripts.battle.states.round_start import RoundStartState
        self.scene.change_state(RoundStartState(self.scene))
