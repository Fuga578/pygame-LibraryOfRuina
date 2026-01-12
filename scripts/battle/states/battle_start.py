from scripts.battle.states.base import BattleState
from scripts.utils.dev_utils import create_sample_cards, create_sample_units
from scripts.models.deck import Deck
from scripts.models.unit import Unit
from copy import deepcopy


class BattleStartState(BattleState):
    """
    戦闘開始ステート

    ・ユニット作成
    ・ユニットの初期手札決定
    """

    def enter(self) -> None:
        print("Enter: BattleStartState")
        self.scene.state_name = "BATTLE START STATE"

        # ユニット作成
        self._create_units()

        # 戦闘開始処理を実行
        self.scene.system.start_battle(
            units=self.scene.allies + self.scene.enemies
        )

        # 次の状態へ遷移
        self._go_next_state()

    def exit(self) -> None:
        self.scene._create_unit_panels()
        print("Exit: BattleStartState")

    def handle(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface) -> None:
        pass

    def _create_units(self):
        # サンプルカードリスト作成
        card_list = create_sample_cards()

        # デッキ作成
        deck = Deck(card_list)

        # ユニット作成
        ally_units = create_sample_units(deck, num=3, is_ally=True)
        self.scene.allies.extend(ally_units)

        enemy_units = create_sample_units(deck, num=3, is_ally=False)
        self.scene.enemies.extend(enemy_units)

    def _go_next_state(self):
        # 次の状態へ遷移
        from scripts.battle.states.round_start import RoundStartState
        self.scene.change_state(RoundStartState(self.scene))
