import os
import pygame


class FontManager:

    def __init__(self, base_dir: str, mapping: dict[str, str]):
        """
        base_dir: フォントファイルが置いてあるディレクトリ
        mapping: {"key": "font_file_name.ttf", ...}
        """
        self.base_dir = base_dir
        self.mapping = mapping
        self._cache: dict[tuple[str, int], pygame.font.Font] = {}

    def get(self, name: str, size: int) -> pygame.font.Font:

        if name not in self.mapping:
            raise KeyError(f"Font name '{name}' is not registered")

        rel_path = self.mapping[name]
        path = os.path.join(self.base_dir, rel_path)

        key = (path, size)
        if key not in self._cache:
            self._cache[key] = pygame.font.Font(path, size)

        return self._cache[key]
