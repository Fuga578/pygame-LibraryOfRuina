import pygame
import math
from enum import Enum, auto
from scripts.battle.states.base import BattleState
from scripts.ui.battle.card import CardView
from scripts.ui.battle.hand import HandView


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

        self.pinned_vel = None  # クリックで固定した味方Vel
        self.pinned_hand = False    # 手札固定判定
        self.selected_hand_card = None  # 選択した手札のカード

        # 手札UI
        self.hand_view = HandView(
            self.scene.game,
            size=(self.scene.game.screen.get_width() - 40, 220),
            pos=(20, 420),
        )
        self.hand_cards_owner = None  # 今表示している手札の持ち主(Unit)

    def exit(self) -> None:
        print("Exit: AllyPlanState")

    def handle(self) -> None:
        print(self.phase)
        if self.scene.game.inputs["left_click_down"]:
            # 戦闘開始ボタン
            if self.scene.battle_start_button.is_hovered(self.scene.game.mouse_pos):
                self._go_next_state()
                return

            mouse_pos = self.scene.game.mouse_pos

            # クリックされた速度ダイスUIを取得（味方/敵どちらも）
            clicked_vel_ui = self._get_hovered_vel_dice_ui(mouse_pos)
            clicked_vel = clicked_vel_ui.velocity_dice if clicked_vel_ui else None

            # クリックした手札のカード
            clicked_card = self.hand_view.get_clicked_card(mouse_pos)

            # 速度ダイス選択フェーズ
            if self.phase == AllyPlanPhase.SELECT_VELOCITY:
                # 味方速度ダイスがクリックされていたら選択開始/手札固定
                if clicked_vel and clicked_vel.owner.is_ally:
                    # 既にカード/ターゲット選択済みのダイスをクリックした場合、選択中のカードを元に戻して再度カード選択
                    if clicked_vel.card is not None:

                        # 巻き戻し
                        self._refund_card_to_hand(clicked_vel)

                        # マッチ判定更新
                        self.scene.clash_infos = self.scene.system.evaluate_clashes(self.scene.all_slots)

                    self.scene.context.selected_vel = clicked_vel   # クリックした速度ダイス保存
                    self.pinned_vel = clicked_vel   # 手札を表示する対象の速度ダイス
                    self.pinned_hand = True         # 手札固定判定
                    self.selected_hand_card = None  # 選択した手札のカードを初期化
                    self.phase = AllyPlanPhase.SELECT_CARD  # 次のフェーズ（手札のカード選択）に遷移

            # カード選択フェーズ
            if self.phase == AllyPlanPhase.SELECT_CARD:
                # 速度ダイスが取得出来ていない場合は最初から
                vel_dice = self.scene.context.selected_vel
                if vel_dice is None:
                    self._finish_current_vel_and_next()
                    return

                ally = vel_dice.owner

                # クリックしたカードがない場合
                if clicked_card is None:
                    return

                # プレイ不可のカードは選択できない
                if not ally.can_play_card(clicked_card):
                    return

                # 光が足りないカードは選択できない
                if not ally.pay_light(clicked_card.cost):
                    return

                # 速度ダイスにカードをセット
                vel_dice.card = clicked_card
                self.scene.context.selected_card = clicked_card
                self.selected_hand_card = clicked_card

                # 手札から選択したカードを削除
                ally.deck.remove_card(clicked_card)

                # 次のフェーズ（ターゲット選択）に遷移
                self.phase = AllyPlanPhase.SELECT_TARGET
                return

            # ターゲット選択フェーズ
            if self.phase == AllyPlanPhase.SELECT_TARGET:

                # 速度ダイスとカードが設定されていない場合は最初から
                vel_dice = self.scene.context.selected_vel
                if vel_dice is None or vel_dice.card is None:
                    self._finish_current_vel_and_next()
                    return

                # 敵速度ダイスをクリックしたらターゲット確定
                if clicked_vel and (not clicked_vel.owner.is_ally):
                    vel_dice.target = clicked_vel
                    self.scene.context.selected_target = clicked_vel

                    # マッチ判定更新
                    self.scene.clash_infos = self.scene.system.evaluate_clashes(self.scene.all_slots)

                    # 次の速度へ
                    self._finish_current_vel_and_next()
                return

        if self.scene.game.inputs["right_click_down"]:
            # 速度ダイス選択フェーズ
            if self.phase == AllyPlanPhase.SELECT_VELOCITY:
                pass
            # カード選択フェーズ
            if self.phase == AllyPlanPhase.SELECT_CARD:
                # 前のフェーズ（速度ダイス選択）に遷移
                self._finish_current_vel_and_next()
            # ターゲット選択フェーズ
            if self.phase == AllyPlanPhase.SELECT_TARGET:
                vel_dice = self.scene.context.selected_vel

                # 選択中のカードがある場合、選択中のカードを元に戻す
                if vel_dice and vel_dice.card:
                    # カードを戻す
                    self._refund_card_to_hand(vel_dice)
                    # マッチ判定更新
                    self.scene.clash_infos = self.scene.system.evaluate_clashes(self.scene.all_slots)

                # 選択したカード初期化
                self.scene.context.selected_card = None
                self.selected_hand_card = None

                # 前のフェーズ（カード選択）に遷移
                self.phase = AllyPlanPhase.SELECT_CARD
                return

    def update(self, dt: float) -> None:
        pass

    def render(self, surface) -> None:
        hovered_vel_dice_ui = self._get_hovered_vel_dice_ui(self.scene.game.mouse_pos)

        # 表示したい手札の持ち主を決める
        hand_owner = None
        # 手札固定時、固定されている手札の持ち主
        if self.pinned_hand and self.pinned_vel:
            hand_owner = self.pinned_vel.owner
        # 速度ダイスホバー時、ホバーしている手札の持ち主
        elif hovered_vel_dice_ui and hovered_vel_dice_ui.velocity_dice.owner.is_ally:
            hand_owner = hovered_vel_dice_ui.velocity_dice.owner

        # 味方手札表示
        if hand_owner is not None:
            self.hand_view.set_hand(hand_owner.deck.hand_cards)
            self.hand_view.render(surface)

        # ホバーした速度ダイスのカード/デッキ表示
        hovered_vel_dice_ui = self._get_hovered_vel_dice_ui(self.scene.game.mouse_pos)
        if hovered_vel_dice_ui:
            owner = hovered_vel_dice_ui.velocity_dice.owner
            # 味方の速度ダイスの場合
            if owner.is_ally:
                pass
            # 敵の速度ダイスの場合
            else:
                card = hovered_vel_dice_ui.velocity_dice.card
                if card is not None:
                    x, y = 20, 420
                    w, h = 320, 160
                    CardView(self.scene.game, card, (w, h), (x, y)).render(surface)

        # マッチ/一方攻撃の矢印を描画
        processed_clash_pairs = set()
        for info in self.scene.clash_infos:
            a_vel = info.attacker
            b_vel = info.defender

            a_vel_ui = self._find_vel_ui(a_vel)
            b_vel_ui = self._find_vel_ui(b_vel)

            if not a_vel_ui or not b_vel_ui:
                continue

            point_a = a_vel_ui.rect.center
            point_b = b_vel_ui.rect.center

            # マッチ判定
            if self.scene.system.is_clash(info):
                # マッチは (A,B) と (B,A) が来ても1回だけ描く
                key = (min(id(a_vel), id(b_vel)), max(id(a_vel), id(b_vel)))
                if key in processed_clash_pairs:
                    continue
                processed_clash_pairs.add(key)

                self._draw_curved_arrow(
                    surface, point_a, point_b,
                    color=(255, 100, 100),
                    width=4,
                    curvature=0.22,
                    arrow_size=12,
                    bidirectional=True
                )
            # 一方攻撃判定
            elif self.scene.system.is_one_sided(info):
                self._draw_curved_arrow(
                    surface, point_a, point_b,
                    color=(100, 100, 255),
                    width=3,
                    curvature=0.22,
                    arrow_size=10,
                    bidirectional=False
                )

    def _select_next_vel_dice(self) -> bool:
        """カード未設定ダイスを取得"""
        for vel_dice in self.scene.ally_slots:
            # チェック済みの場合
            if vel_dice.is_checked:
                continue
            vel_dice.is_checked = True

            if vel_dice.val is None:
                continue
            if vel_dice.owner.is_confused():
                continue
            if vel_dice.card is None:
                self.scene.context.selected_vel = vel_dice
                return True

        return False

    def _finish_current_vel_and_next(self):
        """現在のダイス処理を終了し、次の速度ダイスフェーズへ遷移"""
        self.scene.context.clear_selection()
        self.pinned_vel = None  # クリックで固定した味方Vel
        self.pinned_hand = False  # 手札固定判定
        self.selected_hand_card = None  # 選択した手札のカード
        self.phase = AllyPlanPhase.SELECT_VELOCITY

    def _go_next_state(self):
        # 次の状態へ遷移
        from scripts.battle.states.resolve import ResolveState
        self.scene.change_state(ResolveState(self.scene))

    def _get_hovered_vel_dice_ui(self, mouse_pos):
        for unit_view in self.scene.allies_ui + self.scene.enemies_ui:
            vel_dice_ui = unit_view.get_hovered_vel_dice_ui(mouse_pos)
            if vel_dice_ui:
                return vel_dice_ui
        return None

    def _refund_card_to_hand(self, vel_dice):
        """速度ダイスの選択項目を元に戻す"""
        # 光を戻す
        vel_dice.owner.recover_light(vel_dice.card.cost)
        # カードを手札に戻す
        vel_dice.owner.deck.hand_cards.append(vel_dice.card)

        vel_dice.card = None
        vel_dice.target = None

    def _find_vel_ui(self, vel_dice):
        all_units_ui = self.scene.allies_ui + self.scene.enemies_ui
        for unit_ui in all_units_ui:
            for vel_ui in unit_ui.vel_dice_ui_list:
                if vel_ui.velocity_dice is vel_dice:
                    return vel_ui
        return None

    def _draw_curved_arrow(self, surface, a_pos, b_pos, color, width=3,
                           curvature=0.25, arrow_size=12, bidirectional=False):
        """
        a_pos -> b_pos をカーブ線で描き、矢印を付ける
        - bidirectional=True なら両端に矢印（CLASH用）
        """

        ax, ay = a_pos
        bx, by = b_pos
        dx, dy = bx - ax, by - ay
        dist = math.hypot(dx, dy)
        if dist < 1:
            return

        # 制御点：常に「上」に膨らませる（yを減らす）
        mx, my = (ax + bx) * 0.5, (ay + by) * 0.5
        offset = dist * curvature
        cx, cy = mx, my - offset

        # 2次ベジェを折れ線で近似
        points = []
        steps = max(12, int(dist / 20))
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t) * (1 - t) * ax + 2 * (1 - t) * t * cx + t * t * bx
            y = (1 - t) * (1 - t) * ay + 2 * (1 - t) * t * cy + t * t * by
            points.append((x, y))

        pygame.draw.lines(surface, color, False, points, width)

        # 終点側の矢印
        self._draw_arrow_head(surface, points[-2], points[-1], color, arrow_size)

        # CLASH用：始点側にも矢印（1本の線に両矢印）
        if bidirectional:
            self._draw_arrow_head(surface, points[1], points[0], color, arrow_size)

    def _draw_arrow_head(self, surface, from_pos, to_pos, color, size=12):
        """from_pos -> to_pos の向きに矢印ヘッド（三角）を描く"""
        fx, fy = from_pos
        tx, ty = to_pos
        dx, dy = (tx - fx), (ty - fy)
        ang = math.atan2(dy, dx)

        # 三角形の2点（左右）
        left = (tx - size * math.cos(ang - math.pi / 6),
                ty - size * math.sin(ang - math.pi / 6))
        right = (tx - size * math.cos(ang + math.pi / 6),
                 ty - size * math.sin(ang + math.pi / 6))

        pygame.draw.polygon(surface, color, [(tx, ty), left, right])
