import random
from scripts.models.unit import Unit
from scripts.models.dice import VelocityDice
from enum import Enum, auto
from dataclasses import dataclass


class ClashType(Enum):
    NONE = auto()          # 未設定
    ONE_SIDED = auto()     # 一方攻撃
    CLASH = auto()         # マッチ（衝突）


@dataclass
class ClashInfo:
    attacker: VelocityDice
    defender: VelocityDice
    clash_type: ClashType


class BattleSystem:
    """
    戦闘処理のシステムクラス
    """
    def start_battle(self, units: list[Unit]):
        for unit in units:
            # カードをドロー
            unit.deck.shuffle_draw_pile()
            unit.deck.draw(num=3)

    def start_round(self, units: list[Unit]):
        for unit in units:

            # 光回復
            unit.recover_light(amount=1)

            # 速度ダイス初期化
            for vel_dice in unit.velocity_dice_list:
                vel_dice.init()

            # カードをドロー
            unit.deck.draw(num=1)

            # 混乱していない場合、速度ダイスを振る
            if not unit.is_confused():
                for vel_dice in unit.velocity_dice_list:
                    vel_dice.roll()

    def get_action_order(self, units: list[Unit]):
        vel_dice_list = []
        for unit in units:
            vel_dice_list.extend(unit.velocity_dice_list)

        return sorted(
            vel_dice_list,
            key=lambda v: (v.val is not None, v.val or -1),
            reverse=True
        )

    def plan_enemy(self, enemy_slots: list[VelocityDice], ally_slots: list[VelocityDice]):

        # 速度ダイス順でターゲット選択
        for vel_dice in enemy_slots:
            # ダイスが振られていない場合はスキップ
            if vel_dice.val is None:
                continue

            # ダイスの所有者
            enemy = vel_dice.owner

            # 混乱している場合はスキップ
            if enemy.is_confused():
                continue

            # プレイできるカードのみ抽出
            playable_cards = [card for card in enemy.deck.hand_cards if enemy.can_play_card(card)]

            # プレイできるカードがない場合はスキップ
            if len(playable_cards) <= 0:
                continue

            # カードをランダムに選択
            card = random.choice(playable_cards)
            if not enemy.pay_light(card.cost):
                continue
            enemy.deck.remove_card(card)
            vel_dice.card = card

            # ターゲットをランダムに選択
            target_candidates = [vd for vd in ally_slots]
            target = random.choice(target_candidates)
            vel_dice.target = target

    def evaluate_clashes(self, all_slots: list) -> list[ClashInfo]:
        """マッチ/一方攻撃を判定して返す"""
        infos = []
        for vel_dice in all_slots:

            # ターゲットなしの場合
            if vel_dice.card is None or vel_dice.target is None:
                continue

            # 相互に狙ってたらマッチ
            target = vel_dice.target
            if target.card is not None and target.target is vel_dice:
                infos.append(ClashInfo(vel_dice, target, ClashType.CLASH))
            else:
                infos.append(ClashInfo(vel_dice, target, ClashType.ONE_SIDED))
        return infos

    def resolve_attack(self, all_slots, clash_infos):
        # clash_infos からマッチしているペアを作成
        clash_set = set()
        for info in clash_infos:
            if info.clash_type.name == "CLASH":
                attacker = info.attacker
                defender = info.defender
                clash_set.add((id(attacker), id(defender)))
                clash_set.add((id(defender), id(attacker)))

        for vel_dice in all_slots:
            if vel_dice.val is None or vel_dice.card is None or vel_dice.target is None:
                continue

            attacker = vel_dice.owner
            defender = vel_dice.target.owner
            if attacker.is_dead() or defender.is_dead():
                continue

            # マッチなら “とりあえず相互に1ダメ”
            if (id(vel_dice), id(vel_dice.target)) in clash_set:
                defender.hp = max(0, defender.hp - 1)
                attacker.hp = max(0, attacker.hp - 1)
            else:
                defender.hp = max(0, defender.hp - 1)

    def debug_dump_units(self, units):
        print("=" * 40)
        print("=== BATTLE STATUS DUMP ===")
        for u in units:
            print(f"[{u.name}]")
            print(f"  HP: {u.hp}/{u.max_hp}")
            print(f"  Confusion: {u.confusion_resist}/{u.max_confusion_resist}")
            print(f"  Light: {u.light}/{u.max_light}")

            # 手札
            hand_names = [card.name for card in u.deck.hand_cards]
            print(f"  Hand({len(hand_names)}): {hand_names}")

            # 速度ダイス
            for i, vd in enumerate(u.velocity_dice_list):
                card_name = vd.card.name if vd.card else None
                target_name = vd.target.owner.name if vd.target else None
                print(
                    f"  VelDice[{i}] "
                    f"val={vd.val}, "
                    f"card={card_name}, "
                    f"target={target_name}"
                )
            print("-" * 30)
        print("=" * 40)

