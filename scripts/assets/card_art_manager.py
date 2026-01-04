import os
import pygame
from scripts.utils.img import load_image


# class CardArtManager:
#     """カードサムネ用アセット管理"""
#
#     def __init__(
#         self,
#         base_dir: str,
#         placeholder_path: str | None = None,
#     ):
#         self.base_dir = base_dir
#         self.place_holder_path = placeholder_path
#
#         # 生の画像データ用キャッシュ
#         self._raw_cache = {}
#
#         # スケーリング画像データ用キャッシュ
#         self._scaled_cache = {}
#
#         # placeholder画像
#         self._placeholder = None
#         if placeholder_path:
#             self._placeholder = load_image(self.place_holder_path)
#
#     def _resolve_path(self, card_id):
#         """パスを解決"""
#         file_name = f"{card_id}.png"
#         return os.path.join(self.base_dir, file_name)
#
#     def get_raw(self, card_id: str):
#         """生の画像データを取得"""
#         # キャッシュにある場合はキャッシュを返す
#         if card_id in self._raw_cache:
#             return self._raw_cache[card_id]
#
#         path = self._resolve_path(card_id)
#         if os.path.exists(path):
#             card_surf = load_image(path)
#         else:
#             card_surf = self._placeholder if self._placeholder else pygame.Surface((1, 1), pygame.SRCALPHA)
#
#         self._raw_cache[card_id] = card_surf
#         return card_surf
#
#     def get(self, id: str, size: tuple[int, int] | list[int, int] | None = None):
#         """スケーリングした画像データを取得"""
#
#         # サイズが設定されていない場合はそのままのデータを返す
#         raw_surf = self.get_raw(id)
#         if size is None:
#             return raw_surf
#
#         width = size[0]
#         height = size[1]
#         key = (id, width, height)
#
#         # キャッシュにある場合はキャッシュを返す
#         if key in self._scaled_cache:
#             return self._scaled_cache[key]
#
#         scaled_surf = pygame.transform.smoothscale(raw_surf, size)
#         self._scaled_cache[key] = scaled_surf
#         return scaled_surf
#
#     def clear_scaled_cache(self):
#         self._scaled_cache.clear()



class CardArtManager:
    """カードサムネ用アセット管理"""

    def __init__(
        self,
        base_dir: str,
        placeholder_path: str | None = None,
    ):
        self.base_dir = base_dir
        self.place_holder_path = placeholder_path

        # 生の画像データ用キャッシュ
        self._raw_cache = {}

        # スケーリング画像データ用キャッシュ
        self._scaled_cache = {}

        # placeholder画像
        self._placeholder = None
        if placeholder_path:
            self._placeholder = load_image(self.place_holder_path)

    def _resolve_path(self, card_id):
        """パスを解決"""
        file_name = f"{card_id}.png"
        return os.path.join(self.base_dir, file_name)

    def get_raw(self, card_id: str):
        """生の画像データを取得"""
        # キャッシュにある場合はキャッシュを返す
        if card_id in self._raw_cache:
            return self._raw_cache[card_id]

        # サムネイル画像
        path = self._resolve_path(card_id)
        if os.path.exists(path):
            thumbnail_surf = load_image(path)
        else:
            thumbnail_surf = self._placeholder if self._placeholder else pygame.Surface((1, 1), pygame.SRCALPHA)

        # フレーム画像
        path = self._resolve_path("frame")
        frame_surf = load_image(path)

        frame_surf.blit(thumbnail_surf, (3, 25))

        self._raw_cache[card_id] = frame_surf
        return frame_surf

    def get(self, id: str, scale: float | None = None):
        """スケーリングした画像データを取得"""

        # サイズが設定されていない場合はそのままのデータを返す
        raw_surf = self.get_raw(id)
        if scale is None:
            return raw_surf

        key = (id, scale)

        # キャッシュにある場合はキャッシュを返す
        if key in self._scaled_cache:
            return self._scaled_cache[key]

        scaled_thumbnail_surf = pygame.transform.scale_by(raw_surf, scale)

        self._scaled_cache[key] = scaled_thumbnail_surf
        return scaled_thumbnail_surf

    def clear_scaled_cache(self):
        self._scaled_cache.clear()
