"""Transitions between two pages (pure Python, no Home Assistant imports).

The panel has no transitions of its own. A transition is a short GIF from the old picture to the new
one; its last frame is held long enough for the real page to be uploaded after it. A GIF loops as a
whole, so the frames cannot simply go in front of an animated page.
"""

from __future__ import annotations

import random
from collections.abc import Callable

from PIL import Image

from .render import Rendered

STEPS = 12
FRAME_MS = 50
HOLD_MS = 60_000  # the page is uploaded long before this runs out and the GIF starts over

NONE = "none"
RANDOM = "random"
TRANSITIONS = (NONE, "slide_left", "slide_right", "slide_up", "slide_down", "wipe", "curtain", "blinds", "dissolve",
               "fade", RANDOM)
_DRAWN = tuple(t for t in TRANSITIONS if t not in (NONE, RANDOM))


def pick(kind: str | None, rng: random.Random | None = None) -> str | None:
    """The transition to play: a concrete one, or None for no transition (also for an unknown name)."""
    if kind == RANDOM:
        return (rng or random).choice(_DRAWN)
    return kind if kind in _DRAWN else None


def _ease(t: float) -> float:
    """Slow start and end, so moving pictures do not jerk."""
    return t * t * (3 - 2 * t)


def _slide(dx: int, dy: int) -> Callable[[Image.Image, Image.Image, float], Image.Image]:
    def draw(old: Image.Image, new: Image.Image, t: float) -> Image.Image:
        w, h = old.size
        frac = _ease(t)
        off_x, off_y = round(dx * w * frac), round(dy * h * frac)
        frame = Image.new("RGB", old.size)
        frame.paste(old, (off_x, off_y))
        frame.paste(new, (off_x - dx * w, off_y - dy * h))
        return frame

    return draw


def _masked(reveal: Callable[[int, int, int, int, float], bool]) -> Callable[..., Image.Image]:
    """New picture where reveal(x, y, w, h, t) says so, old picture elsewhere."""

    def draw(old: Image.Image, new: Image.Image, t: float) -> Image.Image:
        w, h = old.size
        mask = Image.new("1", old.size)
        px = mask.load()
        for y in range(h):
            for x in range(w):
                if reveal(x, y, w, h, t):
                    px[x, y] = 1
        return Image.composite(new, old, mask)

    return draw


def _wipe(x: int, _y: int, w: int, _h: int, t: float) -> bool:
    return x < _ease(t) * w


def _curtain(x: int, _y: int, w: int, _h: int, t: float) -> bool:
    return abs(x + 0.5 - w / 2) < _ease(t) * w / 2


def _blinds(x: int, _y: int, _w: int, _h: int, t: float) -> bool:
    return x % 8 < t * 8


def _pixel_order(x: int, y: int) -> float:
    """A fixed random-looking number 0..1 per pixel."""
    return random.Random(x * 1009 + y).random()


def _dissolve(x: int, y: int, _w: int, _h: int, t: float) -> bool:
    return _pixel_order(x, y) < t


def _fade(old: Image.Image, new: Image.Image, t: float) -> Image.Image:
    """Down to black and up again; 16 levels keep the palette of the GIF small."""
    picture, level = (old, 1 - 2 * t) if t < 0.5 else (new, 2 * t - 1)
    steps = round(level * 16)
    return picture.point(lambda v: v * steps // 16)


_DRAW = {
    "slide_left": _slide(-1, 0),
    "slide_right": _slide(1, 0),
    "slide_up": _slide(0, -1),
    "slide_down": _slide(0, 1),
    "wipe": _masked(_wipe),
    "curtain": _masked(_curtain),
    "blinds": _masked(_blinds),
    "dissolve": _masked(_dissolve),
    "fade": _fade,
}


def build(kind: str, old: Image.Image, new: Image.Image) -> Rendered:
    """Frames from old to new, ending on new; kind comes from pick()."""
    old, new = old.convert("RGB"), new.convert("RGB")
    draw = _DRAW[kind]
    frames = [draw(old, new, i / STEPS) for i in range(1, STEPS)] + [new]
    return Rendered(frames, [FRAME_MS] * (STEPS - 1) + [HOLD_MS])


def seconds(rendered: Rendered) -> float:
    """How long the moving part takes: everything but the held last frame."""
    return sum(rendered.durations[:-1]) / 1000
