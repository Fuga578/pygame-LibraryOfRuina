from dataclasses import dataclass
from scripts.models.dice import VelocityDice
from scripts.models.card import Card


@dataclass
class BattleContext:
    """
    戦闘シーンのデータの一時保存用クラス
    """
    selected_vel: VelocityDice | None = None    # 選択中の速度ダイス
    selected_card: Card | None = None   # 選択中のカード
    selected_target_vel: VelocityDice | None = None     # 選択中のターゲット（速度ダイス）

    def clear_selection(self):
        self.selected_vel = None
        self.selected_card = None
        self.selected_target_vel = None
