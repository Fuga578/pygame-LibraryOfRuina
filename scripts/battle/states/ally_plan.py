import random
from enum import Enum, auto
from scripts.battle.states.base import BattleState


class AllyPlanPhase(Enum):
    SELECT_VELOCITY = auto()    # 速度ダイス選択
    SELECT_CARD = auto()        # カード選択
    SELECT_TARGET = auto()      # ターゲット選択


class AllyPlanState(BattleState):
    """
    味方の戦闘準備ステート

    ・速度ダイスを選択
    ・速度ダイスに該当するカードを選択
    ・ターゲット（速度ダイス）を選択
    """

    def enter(self) -> None:
        print("Enter: AllyPlanState")
        self.scene.state_name = "ALLY PLAN STATE"

        self.phase = AllyPlanPhase.SELECT_VELOCITY  # 初期フェーズ
        self.scene.context.clear_selection()    # 初期化

        # 一方攻撃/マッチの判定
        self.scene.clash_infos = self.scene.system.evaluate_clashes(self.scene.all_slots)

    def exit(self) -> None:
        print("Exit: AllyPlanState")

    def handle(self) -> None:
        if not self.scene.game.inputs["left_click_down"]:
            return

        # 速度ダイス選択フェーズ
        if self.phase == AllyPlanPhase.SELECT_VELOCITY:
            # ダイス選択
            self._select_next_vel_dice()

            self.phase = AllyPlanPhase.SELECT_CARD
            return

        # カード選択フェーズ
        if self.phase == AllyPlanPhase.SELECT_CARD:
            vel_dice = self.scene.context.selected_vel
            if vel_dice is None:
                # 次の状態へ遷移
                self._go_next_state()
                return

            ally = vel_dice.owner

            # プレイできるカードのみ抽出
            playable_cards = [card for card in ally.deck.hand_cards if ally.can_play_card(card)]
            if len(playable_cards) <= 0:
                # 次の状態へ遷移
                self._go_next_state()
                return

            # カードをランダムに選択
            card = random.choice(playable_cards)
            vel_dice.card = card
            self.scene.context.selected_card = card

            ally.deck.remove_card(card)

            self.phase = AllyPlanPhase.SELECT_TARGET
            return

        # ターゲット選択フェーズ
        if self.phase == AllyPlanPhase.SELECT_TARGET:
            vel_dice = self.scene.context.selected_vel

            # ターゲットをランダムに選択
            target_candidates = [vd for vd in self.scene.enemy_slots]
            target = random.choice(target_candidates)

            vel_dice.target = target
            self.scene.context.selected_target = target

            # 一方攻撃/マッチの判定更新
            self.scene.clash_infos = self.scene.system.evaluate_clashes(self.scene.all_slots)

            # 次の速度ダイス判定
            self._finish_current_vel_and_next()
            return

    def update(self, dt: float) -> None:
        pass

    def render(self, surface) -> None:
        pass

    def _select_next_vel_dice(self):
        """カード未設定ダイスを取得"""
        for vel_dice in self.scene.ally_slots:
            if vel_dice.val is None:
                continue
            if vel_dice.owner.is_confused():
                continue
            if vel_dice.card is None:
                self.scene.context.selected_vel = vel_dice
                return

    def _finish_current_vel_and_next(self):
        self.scene.context.selected_vel = None
        self.scene.context.selected_card = None
        self.scene.context.selected_target = None
        self.phase = AllyPlanPhase.SELECT_VELOCITY
        self._select_next_vel_dice()

    def _go_next_state(self):
        # 次の状態へ遷移
        from scripts.battle.states.resolve import ResolveState
        self.scene.change_state(ResolveState(self.scene))
