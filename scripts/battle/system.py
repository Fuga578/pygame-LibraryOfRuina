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
        clash_pairs = set()
        for info in clash_infos:
            if self.is_clash(info):
                attacker = info.attacker
                defender = info.defender
                pair = (min(id(attacker), id(defender)), max(id(attacker), id(defender)))
                clash_pairs.add(pair)

        # idから速度ダイスを取得するための辞書
        vel_dice_by_id = {id(v): v for v in all_slots}

        # マッチ済みの速度ダイスID保存用
        processed_vel_ids = set()

        # マッチ処理
        for attacker_id, defender_id in clash_pairs:
            attacker_vel_dice = vel_dice_by_id.get(attacker_id)
            defenter_vel_dice = vel_dice_by_id.get(defender_id)
            if attacker_vel_dice is None or defenter_vel_dice is None:
                continue
            if attacker_vel_dice.val is None or defenter_vel_dice.val is None:
                continue
            if attacker_vel_dice.card is None or defenter_vel_dice.card is None:
                continue
            if attacker_vel_dice.owner.is_dead() or defenter_vel_dice.owner.is_dead():
                continue

            # マッチ
            self._resolve_clash_pair(attacker_vel_dice, defenter_vel_dice)
            processed_vel_ids.add(id(attacker_vel_dice))
            processed_vel_ids.add(id(defenter_vel_dice))

        # 一方攻撃処理（マッチに参加していない速度ダイスのみ）
        for vel_dice in all_slots:
            if id(vel_dice) in processed_vel_ids:
                continue
            if vel_dice.val is None or vel_dice.card is None or vel_dice.target is None:
                continue
            if vel_dice.owner.is_dead() or vel_dice.target.owner.is_dead():
                continue

            # 一方攻撃
            self._resolve_one_sided(vel_dice)

    def is_clash(self, clash_info: ClashInfo):
        return clash_info.clash_type == ClashType.CLASH

    def is_one_sided(self, clash_info: ClashInfo):
        return clash_info.clash_type == ClashType.ONE_SIDED

    def _resolve_clash_pair(self, a_vel_dice, b_vel_dice):
        a_unit = a_vel_dice.owner
        b_unit = b_vel_dice.owner

        a_dices = list(a_vel_dice.card.dice_list)
        b_dices = list(b_vel_dice.card.dice_list)

        while len(a_dices) > 0 and len(b_dices) > 0 \
                and (not a_unit.is_dead() and not a_unit.is_confused()) \
                and (not b_unit.is_dead() and not b_unit.is_confused()):
            a_die = a_dices[0]
            b_die = b_dices[0]

            a_val = a_die.roll()
            b_val = b_die.roll()

            # 攻撃ダイス vs 攻撃ダイス --------------------
            if is_attack(a_die) and is_attack(b_die):
                a_dices.pop(0)
                b_dices.pop(0)
                if a_val > b_val:
                    b_unit.take_damage(damage=a_val, dice_type=a_die.d_type)
                elif a_val < b_val:
                    a_unit.take_damage(damage=b_val, dice_type=b_die.d_type)
                else:
                    pass
            # ------------------------------------------

            # 攻撃ダイス vs 防御ダイス --------------------
            elif is_attack(a_die) and is_block(b_die):
                a_dices.pop(0)
                b_dices.pop(0)
                if a_val > b_val:
                    b_unit.take_damage(damage=a_val - b_val, dice_type=a_die.d_type)
                elif a_val < b_val:
                    a_unit.take_confusion_resist_damage(damage=b_val, dice_type=b_die.d_type)
                else:
                    pass
            elif is_block(a_die) and is_attack(b_die):
                a_dices.pop(0)
                b_dices.pop(0)
                if a_val > b_val:
                    b_unit.take_confusion_resist_damage(damage=a_val, dice_type=a_die.d_type)
                elif a_val < b_val:
                    a_unit.take_damage(damage=b_val - a_val, dice_type=b_die.d_type)
                else:
                    pass
            # ------------------------------------------

            # 攻撃ダイス vs 回避ダイス --------------------
            elif is_attack(a_die) and is_evade(b_die):
                if a_val > b_val:
                    a_dices.pop(0)
                    b_dices.pop(0)
                    b_unit.take_damage(damage=a_val, dice_type=a_die.d_type)
                elif a_val < b_val:
                    a_dices.pop(0)
                    b_unit.heal_confusion_resist(amount=b_val)
                else:
                    pass
            elif is_evade(a_die) and is_attack(b_die):
                if a_val > b_val:
                    b_dices.pop(0)
                    a_unit.heal_confusion_resist(amount=a_val)
                elif a_val < b_val:
                    a_dices.pop(0)
                    b_dices.pop(0)
                    a_unit.take_damage(damage=b_val, dice_type=b_die.d_type)
                else:
                    pass
            # ------------------------------------------

            # 防御ダイス vs 防御ダイス --------------------
            elif is_block(a_die) and is_block(b_die):
                a_dices.pop(0)
                b_dices.pop(0)
                if a_val > b_val:
                    b_unit.take_confusion_resist_damage(damage=a_val, dice_type=a_die.d_type)
                elif a_val < b_val:
                    a_unit.take_confusion_resist_damage(damage=b_val, dice_type=b_die.d_type)
                else:
                    pass
            # ------------------------------------------

            # 防御ダイス vs 回避ダイス --------------------
            elif is_block(a_die) and is_evade(b_die):
                a_dices.pop(0)
                b_dices.pop(0)
                if a_val > b_val:
                    b_unit.take_confusion_resist_damage(damage=a_val, dice_type=a_die.d_type)
                elif a_val < b_val:
                    b_unit.heal_confusion_resist(amount=b_val)
                else:
                    pass
            elif is_evade(a_die) and is_block(b_die):
                a_dices.pop(0)
                b_dices.pop(0)
                if a_val > b_val:
                    a_unit.heal_confusion_resist(amount=a_val)
                elif a_val < b_val:
                    a_unit.take_confusion_resist_damage(damage=b_val, dice_type=b_die.d_type)
                else:
                    pass
            # ------------------------------------------

            # 回避ダイス vs 回避ダイス --------------------
            elif is_evade(a_die) and is_evade(b_die):
                a_dices.pop(0)
                b_dices.pop(0)
            # ------------------------------------------

            # 万一の無限ループ防止
            else:
                a_dices.pop(0)
                b_dices.pop(0)

        if a_unit.is_dead() or b_unit.is_dead():
            return

        # 片方のダイスが尽きたら、残った分は一方攻撃
        if a_dices and not b_dices:
            self._apply_remaining_one_sided(a_unit, b_unit, a_dices)
        elif not a_dices and b_dices:
            self._apply_remaining_one_sided(b_unit, a_unit, b_dices)

    def _apply_remaining_one_sided(self, attacker, defender, dices):
        for die in dices:
            if attacker.is_dead() or defender.is_dead():
                break
            if is_attack(die):
                die_val = die.roll()
                defender.take_damage(damage=die_val, dice_type=die.d_type)
            else:
                attacker.remaining_dices.append(die)

    def _resolve_one_sided(self, vel_dice):
        attacker = vel_dice.owner
        defender = vel_dice.target.owner

        for die in vel_dice.card.dice_list:
            # 攻撃ダイスの場合
            if is_attack(die):
                defender.take_damage(damage=die.roll(), dice_type=die.d_type)
            # 攻撃ダイス以外の場合、使用せずに保存
            else:
                attacker.remaining_dices.append(die)

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

