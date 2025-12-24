from enum import Enum


class Anchor(Enum):
    TOP_LEFT = "topleft"
    TOP_RIGHT = "topright"
    BOTTOM_LEFT = "bottomleft"
    BOTTOM_RIGHT = "bottomright"
    CENTER = "center"
    MID_TOP = "midtop"
    MID_BOTTOM = "midbottom"
    MID_LEFT = "midleft"
    MID_RIGHT = "midright"


def draw_text(surface, font, text, color, pos, anchor: Anchor = Anchor.TOP_LEFT):
    img = font.render(text, True, color)
    rect = img.get_rect()

    if not hasattr(rect, anchor.value):
        raise ValueError(f"Invalid anchor: {anchor}")

    setattr(rect, anchor.value, pos)
    surface.blit(img, rect)


