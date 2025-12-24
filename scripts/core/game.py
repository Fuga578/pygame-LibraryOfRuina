import os
import sys
import pygame
from scripts.core.constants import Constants
from scripts.scene.base import SceneId, SceneManager
from scripts.assets.fonts import FontManager


class Game:

    def __init__(self):
        pygame.init()

        # ウィンドウの設定
        self.screen = pygame.display.set_mode((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))

        # FPSの設定
        self.clock = pygame.time.Clock()

        # 入力
        self.inputs = {
            "left_click": False,
            "left_click_down": False,
            "left_click_up": False,
            "right_click": False,
            "esc": False,
            "enter": False,
            "w": False,
            "a": False,
            "s": False,
            "d": False,
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }

        # フォント
        self.fonts = FontManager(
            base_dir="assets/fonts",
            mapping={
                "dot": "BestTen-DOT.otf",
            }
        )
        self.text_font = self.fonts.get("dot", 18)

        # シーン
        self.scenes = SceneManager(self, SceneId.TITLE)

    def exit(self):
        pygame.quit()
        sys.exit()

    def handle_events(self):

        self.inputs["left_click_down"] = False
        self.inputs["left_click_up"] = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.inputs["esc"] = True
                if event.key == pygame.K_RETURN:
                    self.inputs["enter"] = True
                if event.key == pygame.K_w:
                    self.inputs["w"] = True
                if event.key == pygame.K_a:
                    self.inputs["a"] = True
                if event.key == pygame.K_s:
                    self.inputs["s"] = True
                if event.key == pygame.K_d:
                    self.inputs["d"] = True
                if event.key == pygame.K_UP:
                    self.inputs["up"] = True
                if event.key == pygame.K_DOWN:
                    self.inputs["down"] = True
                if event.key == pygame.K_LEFT:
                    self.inputs["left"] = True
                if event.key == pygame.K_RIGHT:
                    self.inputs["right"] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.inputs["esc"] = False
                if event.key == pygame.K_RETURN:
                    self.inputs["enter"] = False
                if event.key == pygame.K_w:
                    self.inputs["w"] = False
                if event.key == pygame.K_a:
                    self.inputs["a"] = False
                if event.key == pygame.K_s:
                    self.inputs["s"] = False
                if event.key == pygame.K_d:
                    self.inputs["d"] = False
                if event.key == pygame.K_UP:
                    self.inputs["up"] = False
                if event.key == pygame.K_DOWN:
                    self.inputs["down"] = False
                if event.key == pygame.K_LEFT:
                    self.inputs["left"] = False
                if event.key == pygame.K_RIGHT:
                    self.inputs["right"] = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.inputs["left_click"] = True
                    self.inputs["left_click_down"] = True
                if event.button == 3:
                    self.inputs["right_click"] = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.inputs["left_click"] = False
                    self.inputs["left_click_up"] = True
                if event.button == 3:
                    self.inputs["right_click"] = False

    def run(self):
        while True:
            # デルタタイム
            dt = self.clock.tick(Constants.FPS) / 1000.0

            # イベント処理
            self.handle_events()

            # 背景の塗りつぶし
            self.screen.fill(Constants.COLORS["white"])

            # シーンの更新と描画
            self.scenes.handle()
            self.scenes.update(dt)
            self.scenes.render(self.screen)

            # 画面更新
            pygame.display.update()
