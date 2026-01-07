from dataclasses import dataclass
from enum import Enum, auto
from scripts.battle.states.base import BattleState
from scripts.models.dice import VelocityDice, Dice, is_attack, is_block, is_evade
from scripts.battle.system import ClashType
from scripts.models.unit import DamageType, HealType


class ResolvePhase(Enum):
    ROLL = auto()           # ダイスのロールフェーズ
    APPLY = auto()          # ダメージ適用フェーズ


@dataclass
class StepResult:
    """1ステップ結果保持クラス"""
    clash_type: ClashType
    is_use_a_index: bool | None
    a_vel_dice: VelocityDice | None = None
    b_vel_dice: VelocityDice | None = None
    a_die: Dice | None = None
    b_die: Dice | None = None


@dataclass
class ResolverPair:
    """1つの解決単位（マッチ/一方攻撃）"""
    kind: ClashType
    a_vel_dice: VelocityDice
    b_vel_dice: VelocityDice


class ResolveState(BattleState):
    """
    戦闘処理ステート

    ・一方攻撃、マッチ判定
    """

    def enter(self) -> None:
        print("Enter: ResolveState")
        self.scene.state_name = "RESOLVE STATE"

        self.phase = ResolvePhase.ROLL    # 初期フェーズ
        self.step_result: StepResult | None = None  # 1ステップの結果保持用

        # 一方攻撃/マッチの判定更新
        self.scene.clash_infos = self.scene.system.evaluate_clashes(self.scene.all_slots)

        # ステップ駆動用の状態
        self.queue: list[ResolverPair] = self._build_queue()
        self.queue_index = 0

        # 現在処理中のペアのダイス位置
        self.a_index = 0
        self.b_index = 0

    def exit(self) -> None:
        print("Exit: ResolveState")

    def handle(self) -> None:
        if self.scene.game.inputs["left_click_down"]:

            # 全てのマッチ/一方攻撃が終了した場合、次の状態へ遷移
            if self.queue_index >= len(self.queue):
                self._go_next_state()
                return

            # 処理するペア（マッチ/一方攻撃）
            pair = self.queue[self.queue_index]

            # ダイスロールで値を確定するフェーズ --
            if self.phase == ResolvePhase.ROLL:
                done, res = self._roll_one_step(pair)  # 1ダイスだけ処理を進める

                # 現在のペアが終了した場合、次のペアへ
                if done:
                    self.queue_index += 1
                    self.a_index = 0
                    self.b_index = 0
                    return

                # 次のフェーズへ
                self.step_result = res
                self.phase = ResolvePhase.APPLY
                return
            # ---------------------------------

            # ダメージ適用フェーズ ---------------
            if self.phase == ResolvePhase.APPLY:
                self._apply_one_step(self.step_result)  # 1ダイス分だけダメージ判定
                self.step_result = None
                self.phase = ResolvePhase.ROLL
                return
            # ---------------------------------

    def update(self, dt: float) -> None:
        pass

    def render(self, surface) -> None:
        pass

    def _go_next_state(self):
        # 次の状態へ遷移
        from scripts.battle.states.round_start import RoundStartState
        self.scene.change_state(RoundStartState(self.scene))

    def _build_queue(self) -> list[ResolverPair]:
        """マッチ/一方攻撃判定用のリストを取得"""
        queue: list[ResolverPair] = []

        # マッチするペア
        clash_pairs = set()
        for info in self.scene.clash_infos:
            attacker = info.attacker
            defender = info.defender

            # マッチ
            if self.scene.system.is_clash(info):
                pair = (min(id(attacker), id(defender)), max(id(attacker), id(defender)))
                if pair in clash_pairs:
                    continue
                clash_pairs.add(pair)
                queue.append(
                    ResolverPair(
                        kind=ClashType.CLASH,
                        a_vel_dice=attacker,
                        b_vel_dice=defender,
                    )
                )
            # 一方攻撃
            elif self.scene.system.is_one_sided(info):
                queue.append(
                    ResolverPair(
                        kind=ClashType.ONE_SIDED,
                        a_vel_dice=attacker,
                        b_vel_dice=defender,
                    )
                )

        return queue

    def _roll_one_step(self, pair) -> tuple[bool, StepResult | None]:
        """1ダイスだけロール処理"""

        # マッチの場合
        if pair.kind == ClashType.CLASH:
            return self._step_clash_roll(pair)
        # 一方攻撃の場合
        else:
            attacker_vel_dice = pair.a_vel_dice
            defender_vel_dice = pair.b_vel_dice
            return self._step_one_sided_roll(attacker_vel_dice, defender_vel_dice, True)

    def _step_clash_roll(self, pair: ResolverPair) -> tuple[bool, StepResult | None]:
        """マッチ判定1ダイス分"""
        # 速度ダイス
        a_vel_dice = pair.a_vel_dice
        b_vel_dice = pair.b_vel_dice

        # どちらもダイス切れの場合、終了
        if self.a_index >= len(a_vel_dice.card.dice_list) and self.b_index >= len(b_vel_dice.card.dice_list):
            return True, None
        # どちらか一方のみがダイス切れの場合、一方攻撃
        else:
            if self.a_index >= len(a_vel_dice.card.dice_list):
                return self._step_one_sided_roll(attacker_vel_dice=b_vel_dice, defender_vel_dice=a_vel_dice, is_use_a_index=False)
            elif self.b_index >= len(b_vel_dice.card.dice_list):
                return self._step_one_sided_roll(attacker_vel_dice=a_vel_dice, defender_vel_dice=b_vel_dice, is_use_a_index=True)

        # ユニット
        a_unit = a_vel_dice.owner
        b_unit = b_vel_dice.owner

        # どちらかが死亡している場合、終了
        if a_unit.is_dead() or b_unit.is_dead():
            return True, None

        # どちらも混乱状態の場合、終了
        if a_unit.is_confused() and b_unit.is_confused():
            return True, None
        # どちらか一方のみが混乱状態の場合、一方攻撃
        else:
            if a_unit.is_confused():
                return self._step_one_sided_roll(attacker_vel_dice=b_vel_dice, defender_vel_dice=a_vel_dice, is_use_a_index=False)
            elif b_unit.is_confused():
                return self._step_one_sided_roll(attacker_vel_dice=a_vel_dice, defender_vel_dice=b_vel_dice, is_use_a_index=True)

        # ダイス一覧
        a_dices = list(a_vel_dice.card.dice_list)
        b_dices = list(b_vel_dice.card.dice_list)

        # ダイス
        a_die = a_dices[self.a_index]
        b_die = b_dices[self.b_index]

        # ダイスロール
        a_die.roll()
        b_die.roll()

        res = StepResult(
            clash_type=ClashType.CLASH,
            is_use_a_index=None,
            a_vel_dice=a_vel_dice,
            b_vel_dice=b_vel_dice,
            a_die=a_die,
            b_die=b_die,
        )

        return False, res

    def _step_one_sided_roll(self, attacker_vel_dice, defender_vel_dice, is_use_a_index) -> tuple[bool, StepResult | None]:
        """一方攻撃判定1ダイス分"""
        idx = self.a_index if is_use_a_index else self.b_index

        # ダイス切れなら終了
        if idx >= len(attacker_vel_dice.card.dice_list):
            return True, None

        attacker = attacker_vel_dice.owner
        defender = defender_vel_dice.owner

        # 攻撃者が混乱している場合は終了
        if attacker.is_confused():
            return True, None

        # どちらかが死亡していた場合は終了
        if attacker.is_dead() or defender.is_dead():
            return True, None

        # 攻撃者のダイス
        a_dices = list(attacker_vel_dice.card.dice_list)
        a_die = a_dices[idx]

        # TODO: 攻撃ダイスの場合はダイスロール
        a_die.roll()
        # TODO: 攻撃ダイス以外の場合は使用せずに保持

        res = StepResult(
            clash_type=ClashType.ONE_SIDED,
            is_use_a_index=is_use_a_index,
            a_vel_dice=attacker_vel_dice,
            b_vel_dice=defender_vel_dice,
            a_die=a_die,
            b_die=None,
        )

        return False, res

    def _apply_one_step(self, res: StepResult | None):
        if res is None:
            return

        # マッチ
        if res.clash_type == ClashType.CLASH:
            self._step_clash_apply(res)
        # 一方攻撃
        else:
            self._step_one_sided_apply(res)

    def _step_clash_apply(self, res: StepResult | None):
        if res is None:
            return

        a_unit = res.a_vel_dice.owner
        b_unit = res.b_vel_dice.owner
        a_die = res.a_die
        b_die = res.b_die
        a_val = a_die.val
        b_val = b_die.val

        # 攻撃ダイス vs 攻撃ダイス --------------------
        if is_attack(a_die) and is_attack(b_die):
            self.a_index += 1
            self.b_index += 1
            if a_val > b_val:
                hp_damage, confusion_damage = b_unit.take_damage(damage=a_val, dice_type=a_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
                unit_ui.on_damage(hp_damage, DamageType.HP)
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            elif a_val < b_val:
                hp_damage, confusion_damage = a_unit.take_damage(damage=b_val, dice_type=b_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(a_unit)]
                unit_ui.on_damage(hp_damage, DamageType.HP)
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            else:
                pass
        # ------------------------------------------

        # 攻撃ダイス vs 防御ダイス --------------------
        elif is_attack(a_die) and is_block(b_die):
            self.a_index += 1
            self.b_index += 1
            if a_val > b_val:
                hp_damage, confusion_damage = b_unit.take_damage(damage=a_val - b_val, dice_type=a_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
                unit_ui.on_damage(hp_damage, DamageType.HP)
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            elif a_val < b_val:
                confusion_damage = a_unit.take_confusion_resist_damage(damage=b_val, dice_type=b_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(a_unit)]
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            else:
                pass
        elif is_block(a_die) and is_attack(b_die):
            self.a_index += 1
            self.b_index += 1
            if a_val > b_val:
                confusion_damage = b_unit.take_confusion_resist_damage(damage=a_val, dice_type=a_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            elif a_val < b_val:
                hp_damage, confusion_damage = a_unit.take_damage(damage=b_val - a_val, dice_type=b_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(a_unit)]
                unit_ui.on_damage(hp_damage, DamageType.HP)
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            else:
                pass
        # ------------------------------------------

        # 攻撃ダイス vs 回避ダイス --------------------
        elif is_attack(a_die) and is_evade(b_die):
            if a_val > b_val:
                self.a_index += 1
                self.b_index += 1
                hp_damage, confusion_damage = b_unit.take_damage(damage=a_val, dice_type=a_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
                unit_ui.on_damage(hp_damage, DamageType.HP)
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            elif a_val < b_val:
                self.a_index += 1
                b_unit.heal_confusion_resist(amount=b_val)

                unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
                unit_ui.on_heal(b_val, HealType.CONFUSION)
            else:
                self.a_index += 1
                self.b_index += 1
        elif is_evade(a_die) and is_attack(b_die):
            if a_val > b_val:
                self.b_index += 1
                a_unit.heal_confusion_resist(amount=a_val)

                unit_ui = self.scene.unit_ui_id_map[id(a_unit)]
                unit_ui.on_heal(a_val, HealType.CONFUSION)
            elif a_val < b_val:
                self.a_index += 1
                self.b_index += 1
                hp_damage, confusion_damage = a_unit.take_damage(damage=b_val, dice_type=b_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(a_unit)]
                unit_ui.on_damage(hp_damage, DamageType.HP)
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            else:
                self.a_index += 1
                self.b_index += 1
        # ------------------------------------------

        # 防御ダイス vs 防御ダイス --------------------
        elif is_block(a_die) and is_block(b_die):
            self.a_index += 1
            self.b_index += 1
            if a_val > b_val:
                confusion_damage = b_unit.take_confusion_resist_damage(damage=a_val, dice_type=a_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            elif a_val < b_val:
                confusion_damage = a_unit.take_confusion_resist_damage(damage=b_val, dice_type=b_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(a_unit)]
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            else:
                pass
        # ------------------------------------------

        # 防御ダイス vs 回避ダイス --------------------
        elif is_block(a_die) and is_evade(b_die):
            self.a_index += 1
            self.b_index += 1
            if a_val > b_val:
                confusion_damage = b_unit.take_confusion_resist_damage(damage=a_val, dice_type=a_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            elif a_val < b_val:
                b_unit.heal_confusion_resist(amount=b_val)

                unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
                unit_ui.on_heal(b_val, HealType.CONFUSION)
            else:
                pass
        elif is_evade(a_die) and is_block(b_die):
            self.a_index += 1
            self.b_index += 1
            if a_val > b_val:
                a_unit.heal_confusion_resist(amount=a_val)

                unit_ui = self.scene.unit_ui_id_map[id(a_unit)]
                unit_ui.on_heal(a_val, HealType.CONFUSION)
            elif a_val < b_val:
                confusion_damage = a_unit.take_confusion_resist_damage(damage=b_val, dice_type=b_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(a_unit)]
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            else:
                pass
        # ------------------------------------------

        # 回避ダイス vs 回避ダイス --------------------
        elif is_evade(a_die) and is_evade(b_die):
            self.a_index += 1
            self.b_index += 1
        # ------------------------------------------

        return False

    def _step_one_sided_apply(self, res: StepResult | None):
        if res is None:
            return

        a_unit = res.a_vel_dice.owner
        b_unit = res.b_vel_dice.owner
        a_die = res.a_die

        if res.is_use_a_index:
            self.a_index += 1
        else:
            self.b_index += 1

        # 攻撃ダイスの場合
        if is_attack(a_die):
            b_unit.take_damage(damage=a_die.val, dice_type=a_die.d_type)
        # 攻撃ダイス以外の場合、使用せずに保存
        else:
            a_unit.remaining_dices.append(a_die)
