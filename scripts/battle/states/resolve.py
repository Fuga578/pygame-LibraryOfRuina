import pygame
from dataclasses import dataclass
from enum import Enum, auto
from scripts.battle.states.base import BattleState
from scripts.models.dice import VelocityDice, DiceType, Dice, is_attack, is_block, is_evade
from scripts.battle.system import ClashType
from scripts.models.unit import DamageType, HealType


class ResolvePhase(Enum):
    PREPARE = auto()        # 準備フェーズ
    ROLL = auto()           # ダイスのロールフェーズ
    APPLY = auto()          # ダメージ適用フェーズ
    HOLD = auto()           # 結果固定表示フェーズ


@dataclass
class StepResult:
    """1ステップ結果保持クラス"""
    clash_type: ClashType
    is_use_a_index: bool | None
    a_vel_dice: VelocityDice | None = None
    b_vel_dice: VelocityDice | None = None
    a_die: Dice | None = None
    b_die: Dice | None = None
    a_roll: int | None = None
    b_roll: int | None = None


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

        self.phase = ResolvePhase.PREPARE    # 初期フェーズ
        self.step_result: StepResult | None = None  # 1ステップの結果保持用

        # 一方攻撃/マッチの判定更新
        self.scene.clash_infos = self.scene.system.evaluate_clashes(self.scene.all_slots)

        # ステップ駆動用の状態
        self.queue: list[ResolverPair] = self._build_queue()
        self.queue_index = 0

        self.is_next_phase = False

        # 現在処理中のペアのダイス位置
        self.a_index = 0
        self.b_index = 0
        self.diff_a_index = 0
        self.diff_b_index = 0

        self.dt = 0.0
        self.roll_timer = 0.0   # ダイスロール結果表示タイマー

    def exit(self) -> None:
        print("Exit: ResolveState")

    def handle(self) -> None:
        if self.scene.game.inputs["left_click_down"]:
            pass
            # # 全てのマッチ/一方攻撃が終了した場合、次の状態へ遷移
            # if self.queue_index >= len(self.queue):
            #     self._go_next_state()
            #     return
            #
            # # 処理するペア（マッチ/一方攻撃）
            # pair = self.queue[self.queue_index]
            #
            # # マッチ/一方攻撃準備フェーズ
            # if self.phase == ResolvePhase.PREPARE:
            #     done, res = self._prepare_one_step(pair)  # 1ダイスだけ処理を進める
            #
            #     # 現在のペアが終了した場合、次のペアへ
            #     if done:
            #         self.queue_index += 1
            #         self.a_index = 0
            #         self.b_index = 0
            #         return
            #
            #     # 終了していないのに結果がない場合
            #     if res is None:
            #         return
            #
            #     # 次のフェーズへ
            #     self.step_result = res
            #     self.phase = ResolvePhase.ROLL
            #     return
            #
            # # ダイスロールで値を確定するフェーズ --
            # if self.phase == ResolvePhase.ROLL:
            #     # ダイスロール実行
            #     self._confirm_roll(self.step_result)
            #
            #     # 次のフェーズへ
            #     self.phase = ResolvePhase.APPLY
            #     return
            # # ---------------------------------
            #
            # # ダメージ適用フェーズ ---------------
            # if self.phase == ResolvePhase.APPLY:
            #     self.diff_a_index, self.diff_b_index = self._apply_one_step(self.step_result)  # 1ダイス分だけダメージ判定
            #     self.phase = ResolvePhase.HOLD
            #     return
            # # ---------------------------------
            #
            # # 結果固定表示フェーズ ---------------
            # if self.phase == ResolvePhase.HOLD:
            #     # 表示は残したまま
            #     self.step_result = None
            #     self.a_index += self.diff_a_index
            #     self.b_index += self.diff_b_index
            #     self.diff_a_index = 0
            #     self.diff_b_index = 0
            #     self.phase = ResolvePhase.PREPARE
            #     return
            # # ---------------------------------

    def update(self, dt: float) -> None:

        # UI表示 ==============================
        if self.queue_index < len(self.queue):
            pair = self.queue[self.queue_index]

            active_units_name = {
                pair.a_vel_dice.owner.name,
                pair.b_vel_dice.owner.name,
            }
            for unit_ui in self.scene.allies_ui + self.scene.enemies_ui:
                unit_ui.is_dimmed = True
                if unit_ui.unit.name in active_units_name:
                    unit_ui.is_dimmed = False
        # =====================================

        # マッチ/一方攻撃処理 ===================
        # 全てのマッチ/一方攻撃が終了した場合、次の状態へ遷移
        if self.queue_index >= len(self.queue):
            self._go_next_state()
            return

        # 処理するペア（マッチ/一方攻撃）
        pair = self.queue[self.queue_index]

        # マッチ/一方攻撃準備フェーズ
        if self.phase == ResolvePhase.PREPARE:
            # 次のフェーズへ
            if self.is_next_phase and self.scene.game.inputs["left_click_down"]:
                self.is_next_phase = False
                self.phase = ResolvePhase.ROLL
            else:
                done, res = self._prepare_one_step(pair)  # 1ダイスだけ処理を進める

                # 現在のペアが終了した場合、次のペアへ
                if done:
                    self.queue_index += 1
                    self.a_index = 0
                    self.b_index = 0
                    return

                # 終了していないのに結果がない場合
                if res is None:
                    return

                self.step_result = res
                self.is_next_phase = True

            return

        # ダイスロールで値を確定するフェーズ --
        if self.phase == ResolvePhase.ROLL:
            self.dt += dt
            # 次のフェーズへ
            if self.is_next_phase:
                if self.dt >= 0.5:
                    self.is_next_phase = False
                    self.dt = 0.0
                    self.phase = ResolvePhase.APPLY
            else:
                # ダイスロール実行
                self._confirm_roll(self.step_result)
                self.is_next_phase = True
            return
        # ---------------------------------

        # ダメージ適用フェーズ ---------------
        if self.phase == ResolvePhase.APPLY:
            self.dt += dt
            # 次のフェーズへ
            if self.is_next_phase:
                if self.dt >= 1.0:
                    self.is_next_phase = False
                    self.dt = 0.0
                    self.phase = ResolvePhase.HOLD
            else:
                self.diff_a_index, self.diff_b_index = self._apply_one_step(self.step_result)  # 1ダイス分だけダメージ判定
                self.is_next_phase = True
            return
        # ---------------------------------

        # 結果固定表示フェーズ ---------------
        if self.phase == ResolvePhase.HOLD:
            # 次のフェーズへ
            if self.is_next_phase:
                self.is_next_phase = False
                self.phase = ResolvePhase.PREPARE
            else:
                self.step_result = None
                self.a_index += self.diff_a_index
                self.b_index += self.diff_b_index
                self.diff_a_index = 0
                self.diff_b_index = 0
                self.is_next_phase = True
            return
        # ---------------------------------
        # =====================================

    def render(self, surface):
        if self.queue_index >= len(self.queue):
            return

        pair = self.queue[self.queue_index]

        # ダイス一覧（pairから取る）
        a_dices = pair.a_vel_dice.card.dice_list if pair.a_vel_dice and pair.a_vel_dice.card else []
        b_dices = pair.b_vel_dice.card.dice_list if pair.b_vel_dice and pair.b_vel_dice.card else []

        left = pygame.Rect(40, 40, 320, 80)
        right = pygame.Rect(surface.get_width() - 360, 40, 320, 80)

        if pair.a_vel_dice.owner.is_ally:
            self._render_dice_list(surface, right, a_dices, self.a_index, pair.a_vel_dice.owner.name)
            if pair.kind == ClashType.CLASH:
                self._render_dice_list(surface, left, b_dices, self.b_index, pair.b_vel_dice.owner.name)
        else:
            self._render_dice_list(surface, left, a_dices, self.a_index, pair.a_vel_dice.owner.name)
            if pair.kind == ClashType.CLASH:
                self._render_dice_list(surface, right, b_dices, self.b_index, pair.b_vel_dice.owner.name)

    def _go_next_state(self):
        # 次の状態へ遷移
        from scripts.battle.states.round_start import RoundStartState
        self.scene.change_state(RoundStartState(self.scene))

    def _render_dice_list(self, surface, rect, dices, idx, title):
        font = self.scene.game.fonts.get("dot", 20)
        pygame.draw.rect(surface, (20, 20, 20), rect, border_radius=8)
        pygame.draw.rect(surface, (220, 220, 220), rect, 2, border_radius=8)

        surface.blit(font.render(title, True, (255, 255, 255)), (rect.x + 8, rect.y + 6))

        x = rect.x + 10
        y = rect.y + 34
        size = 22
        gap = 12

        for i in range(idx, len(dices)):
            d = dices[i]
            box = pygame.Rect(x + (i - idx) * (size + gap), y, size, size)

            self.icon = None
            if d.d_type == DiceType.SLASH:
                self.icon = self.scene.game.assets["slash_icon"]
            elif d.d_type == DiceType.PIERCE:
                self.icon = self.scene.game.assets["pierce_icon"]
            elif d.d_type == DiceType.BLUNT:
                self.icon = self.scene.game.assets["blunt_icon"]
            elif d.d_type == DiceType.BLOCK:
                self.icon = self.scene.game.assets["block_icon"]
            elif d.d_type == DiceType.EVADE:
                self.icon = self.scene.game.assets["evade_icon"]

            if d.val is None:
                surface.blit(self.icon, (box.centerx - self.icon.get_width() // 2, box.centery - self.icon.get_height() // 2 + 8))
            else:
                self.dice_icon = self.scene.game.assets["vel_dice"]
                surface.blit(self.dice_icon, (box.centerx - self.icon.get_width() // 2, box.centery - self.icon.get_height() // 2 + 8))

                font = self.scene.game.fonts.get("dot", 16)
                surf = font.render(f"{d.val}", True, (0, 0, 0))
                surface.blit(surf, (box.centerx - surf.get_width() // 2, box.centery - surf.get_height() // 2 + 8))

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

    def _get_roll_panel_rect(self, unit_view_rect: pygame.Rect, side: str) -> pygame.Rect:
        w, h = 260, 140
        y = unit_view_rect.centery - h // 2
        if side == "left":
            x = unit_view_rect.left - 20 - w
        else:
            x = unit_view_rect.right + 20
        return pygame.Rect(x, y, w, h)

    def _confirm_roll(self, res: StepResult):
        if res is None:
            return

        if res.a_die and res.a_roll is None:
            res.a_roll = res.a_die.roll()
        if res.b_die and res.b_roll is None:
            res.b_roll = res.b_die.roll()

    def _prepare_one_step(self, pair) -> tuple[bool, StepResult | None]:
        """1ダイスだけロール処理"""

        # マッチの場合
        if pair.kind == ClashType.CLASH:
            return self._step_clash_prepare(pair)
        # 一方攻撃の場合
        else:
            attacker_vel_dice = pair.a_vel_dice
            defender_vel_dice = pair.b_vel_dice
            return self._step_one_sided_prepare(attacker_vel_dice, defender_vel_dice, True)

    def _step_clash_prepare(self, pair: ResolverPair) -> tuple[bool, StepResult | None]:
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
                return self._step_one_sided_prepare(attacker_vel_dice=b_vel_dice, defender_vel_dice=a_vel_dice, is_use_a_index=False)
            elif self.b_index >= len(b_vel_dice.card.dice_list):
                return self._step_one_sided_prepare(attacker_vel_dice=a_vel_dice, defender_vel_dice=b_vel_dice, is_use_a_index=True)

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
                return self._step_one_sided_prepare(attacker_vel_dice=b_vel_dice, defender_vel_dice=a_vel_dice, is_use_a_index=False)
            elif b_unit.is_confused():
                return self._step_one_sided_prepare(attacker_vel_dice=a_vel_dice, defender_vel_dice=b_vel_dice, is_use_a_index=True)

        # ダイス一覧
        a_dices = list(a_vel_dice.card.dice_list)
        b_dices = list(b_vel_dice.card.dice_list)

        # ダイス
        a_die = a_dices[self.a_index]
        b_die = b_dices[self.b_index]

        res = StepResult(
            clash_type=ClashType.CLASH,
            is_use_a_index=None,
            a_vel_dice=a_vel_dice,
            b_vel_dice=b_vel_dice,
            a_die=a_die,
            b_die=b_die,
        )

        return False, res

    def _step_one_sided_prepare(self, attacker_vel_dice, defender_vel_dice, is_use_a_index) -> tuple[bool, StepResult | None]:
        """一方攻撃判定1ダイス分"""
        idx = self.a_index if is_use_a_index else self.b_index

        # ダイス切れなら終了
        if idx >= len(attacker_vel_dice.card.dice_list):
            return True, None

        attacker = attacker_vel_dice.owner
        defender = defender_vel_dice.owner

        # 攻撃者のダイス
        a_dices = list(attacker_vel_dice.card.dice_list)
        a_die = a_dices[idx]

        # 攻撃ダイス以外の場合
        if not is_attack(a_die):
            attacker.remaining_dices.append(a_die)
            if is_use_a_index:
                self.a_index += 1
            else:
                self.b_index += 1
            return False, None

        # 攻撃者が混乱している場合は終了
        if attacker.is_confused():
            return True, None

        # どちらかが死亡していた場合は終了
        if attacker.is_dead() or defender.is_dead():
            return True, None

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
        diff_a_index = 0
        diff_b_index = 0
        if res is None:
            return diff_a_index, diff_b_index

        # マッチ
        if res.clash_type == ClashType.CLASH:
            diff_a_index, diff_b_index = self._step_clash_apply(res)
        # 一方攻撃
        else:
            diff_a_index, diff_b_index = self._step_one_sided_apply(res)

        return diff_a_index, diff_b_index

    def _step_clash_apply(self, res: StepResult | None):
        diff_a_index = 0
        diff_b_index = 0
        if res is None:
            return diff_a_index, diff_b_index

        a_unit = res.a_vel_dice.owner
        b_unit = res.b_vel_dice.owner
        a_die = res.a_die
        b_die = res.b_die
        a_val = a_die.val
        b_val = b_die.val

        # 攻撃ダイス vs 攻撃ダイス --------------------
        if is_attack(a_die) and is_attack(b_die):
            diff_a_index = 1
            diff_b_index = 1
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
            diff_a_index = 1
            diff_b_index = 1
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
            diff_a_index = 1
            diff_b_index = 1
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
                diff_a_index = 1
                diff_b_index = 1
                hp_damage, confusion_damage = b_unit.take_damage(damage=a_val, dice_type=a_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
                unit_ui.on_damage(hp_damage, DamageType.HP)
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            elif a_val < b_val:
                diff_a_index = 1
                b_unit.heal_confusion_resist(amount=b_val)

                unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
                unit_ui.on_heal(b_val, HealType.CONFUSION)
            else:
                diff_a_index = 1
                diff_b_index = 1
        elif is_evade(a_die) and is_attack(b_die):
            if a_val > b_val:
                diff_b_index = 1
                a_unit.heal_confusion_resist(amount=a_val)

                unit_ui = self.scene.unit_ui_id_map[id(a_unit)]
                unit_ui.on_heal(a_val, HealType.CONFUSION)
            elif a_val < b_val:
                diff_a_index = 1
                diff_b_index = 1
                hp_damage, confusion_damage = a_unit.take_damage(damage=b_val, dice_type=b_die.d_type)

                unit_ui = self.scene.unit_ui_id_map[id(a_unit)]
                unit_ui.on_damage(hp_damage, DamageType.HP)
                unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
            else:
                diff_a_index = 1
                diff_b_index = 1
        # ------------------------------------------

        # 防御ダイス vs 防御ダイス --------------------
        elif is_block(a_die) and is_block(b_die):
            diff_a_index = 1
            diff_b_index = 1
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
            diff_a_index = 1
            diff_b_index = 1
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
            diff_a_index = 1
            diff_b_index = 1
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
            diff_a_index = 1
            diff_b_index = 1
        # ------------------------------------------

        return diff_a_index, diff_b_index

    def _step_one_sided_apply(self, res: StepResult | None):
        diff_a_index = 0
        diff_b_index = 0
        if res is None:
            return diff_a_index, diff_b_index

        a_unit = res.a_vel_dice.owner
        b_unit = res.b_vel_dice.owner
        a_die = res.a_die

        if res.is_use_a_index:
            diff_a_index = 1
        else:
            diff_b_index = 1

        # 攻撃ダイスの場合
        if is_attack(a_die):
            hp_damage, confusion_damage = b_unit.take_damage(damage=a_die.val, dice_type=a_die.d_type)

            unit_ui = self.scene.unit_ui_id_map[id(b_unit)]
            unit_ui.on_damage(hp_damage, DamageType.HP)
            unit_ui.on_damage(confusion_damage, DamageType.CONFUSION)
        # 攻撃ダイス以外の場合、使用せずに保存
        else:
            a_unit.remaining_dices.append(a_die)

        return diff_a_index, diff_b_index
