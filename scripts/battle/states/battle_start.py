from scripts.battle.states.base import BattleState
from scripts.utils.dev_utils import create_sample_cards
from scripts.models.deck import Deck
from scripts.models.unit import Unit


class BattleStartState(BattleState):
    """
    戦闘開始ステート

    ・ユニット作成
    ・ユニットの初期手札決定
    """

    def enter(self) -> None:
        print("Enter: BattleStartState")
        self.scene.state_name = "BATTLE START STATE"

    def exit(self) -> None:
        print("Exit: BattleStartState")

    def handle(self) -> None:
        if self.scene.game.inputs["left_click_down"]:

            # ユニット作成
            self._create_units()

            # 戦闘開始処理を実行
            self.scene.system.start_battle(
                units=self.scene.allies + self.scene.enemies
            )

            # 次の状態へ遷移
            self._go_next_state()

    def update(self, dt: float) -> None:
        pass

    def render(self, surface) -> None:
        pass

    def _create_units(self):
        # サンプルカードリスト作成
        card_list = create_sample_cards()

        # デッキ作成
        ally_deck = Deck(card_list)
        enemy_deck = Deck(card_list)

        # ユニット作成
        ally1 = Unit(
            name="Ally1",
            max_hp=30,
            max_confusion_resist=10,
            max_light=3,
            min_speed=1,
            max_speed=6,
            deck=ally_deck,
            is_ally=True,
        )
        self.scene.allies = [ally1]

        enemy1 = Unit(
            name="Enemy1",
            max_hp=30,
            max_confusion_resist=10,
            max_light=3,
            min_speed=1,
            max_speed=6,
            deck=enemy_deck,
            is_ally=False,
        )
        self.scene.enemies = [enemy1]

    def _go_next_state(self):
        # 次の状態へ遷移
        from scripts.battle.states.round_start import RoundStartState
        self.scene.change_state(RoundStartState(self.scene))
