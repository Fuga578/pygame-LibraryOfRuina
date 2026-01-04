import random
from scripts.models.unit import Unit
from scripts.models.dice import VelocityDice, is_attack, is_block, is_evade
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque


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
            target_candidates = [vel_dice for vel_dice in ally_slots]
            target = random.choice(target_candidates)
            vel_dice.target = target

    def evaluate_clashes(self, all_slots: list) -> list[ClashInfo]:
        """マッチ/一方攻撃を判定して返す"""

        infos: list[ClashInfo] = []

        # 有効な速度ダイス
        active = [vel_dice for vel_dice in all_slots
                  if vel_dice.card is not None and vel_dice.target is not None and vel_dice.val is not None]

        # key: 狙われた側の速度ダイス, val: 狙う側の速度ダイス
        incoming: dict = {}
        for a in active:
            incoming.setdefault(a.target, []).append(a)

        # 最終的な対戦相手dict
        final_opponent: dict = {}  # vel_dice -> vel_dice
        used = set()  # 既にマッチに採用された vel_dice

        def order_key(vel_dice):
            # 選択順がない(敵など)場合は0
            return (getattr(vel_dice, "select_order", 0), vel_dice.val)

        # 狙われた側の速度ダイスごとに、誰とマッチするかを決める
        for defender, attackers in incoming.items():
            # 既にマッチ済みの場合
            if defender in used:
                continue
            if defender.card is None or defender.val is None:
                continue

            # 既に使われてない攻撃者だけ
            cand = [a for a in attackers if a not in used and a.val is not None]

            chosen = None

            # マッチ奪い判定：defender より速度が高い attacker がいれば割り込み可能（味方のみ）
            interceptors = [a for a in cand if a.val > defender.val and a.owner.is_ally]
            if interceptors:
                # 最後に選択したもの優先
                chosen = max(interceptors, key=order_key)

            # マッチ奪いが無い場合のみ、相互狙いならマッチ判定
            if chosen is None:
                mutuals = [a for a in cand if defender.target is a]
                if mutuals:
                    chosen = max(mutuals, key=order_key)

            # マッチ確定
            if chosen is not None:
                used.add(defender)
                used.add(chosen)
                final_opponent[chosen] = defender
                final_opponent[defender] = chosen

        # マッチ判定を算出
        for a in active:
            d = a.target
            # マッチに参加している速度ダイスはマッチ処理
            if a in final_opponent:
                opp = final_opponent[a]
                infos.append(ClashInfo(a, opp, ClashType.CLASH))
            else:
                # マッチに参加してない速度ダイスは一方攻撃（元targetへ）
                infos.append(ClashInfo(a, d, ClashType.ONE_SIDED))

        return infos

    def is_clash(self, clash_info: ClashInfo):
        return clash_info.clash_type == ClashType.CLASH

    def is_one_sided(self, clash_info: ClashInfo):
        return clash_info.clash_type == ClashType.ONE_SIDED

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
            for i, vel_dice in enumerate(u.velocity_dice_list):
                card_name = vel_dice.card.name if vel_dice.card else None
                target_name = vel_dice.target.owner.name if vel_dice.target else None
                print(
                    f"  VelDice[{i}] "
                    f"val={vel_dice.val}, "
                    f"card={card_name}, "
                    f"target={target_name}"
                )
            print("-" * 30)
        print("=" * 40)

