class ConstantMeta(type):
    def __setattr__(cls, name, value):
        """定数の追加・上書きを禁止します。"""
        if name in cls.__dict__:
            raise AttributeError(f"定数 '{name}' は上書きできません。")
        raise AttributeError(f"定数 '{name}' は追加できません。")

    def __call__(cls, *args, **kwargs):
        """クラスのインスタンス化を禁止します。"""
        raise TypeError(f"{cls.__name__} はインスタンス化できません。")


class Constants(metaclass=ConstantMeta):

    # ゲーム画面の幅
    SCREEN_WIDTH: int = 1280

    # ゲーム画面の高さ
    SCREEN_HEIGHT: int = 720

    # FPS
    FPS: int = 60

    # 色
    COLORS: dict[str, tuple] = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
    }

    # フォント
    FONT_PATH: str = "assets/font/BestTen-DOT.otf"
