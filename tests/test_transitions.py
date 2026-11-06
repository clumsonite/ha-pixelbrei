"""Page transitions: frames, timing and size of the GIF."""

import random

import pytest
from PIL import Image
from pixel_clock import icons, render, transitions
from pixel_clock.render import Line, Screen, frame_at

W, H = 64, 16
DRAWN = [t for t in transitions.TRANSITIONS if t not in (transitions.NONE, transitions.RANDOM)]


def _pages():
    old = render.render_screen(Screen([Line("11°")], icon=icons.builtin_icon("sun")), W, H)
    new = render.render_screen(Screen([Line("Hallo")], icon=icons.builtin_icon("heart")), W, H)
    return old.frames[0], new.frames[0]


@pytest.mark.parametrize("kind", DRAWN)
def test_transition_ends_on_the_new_page_and_holds_it(kind):
    old, new = _pages()
    r = transitions.build(kind, old, new)
    assert len(r.frames) == transitions.STEPS
    assert all(f.size == (W, H) for f in r.frames)
    assert r.frames[-1].tobytes() == new.convert("RGB").tobytes()
    assert r.durations[-1] == transitions.HOLD_MS
    assert transitions.seconds(r) == pytest.approx((transitions.STEPS - 1) * transitions.FRAME_MS / 1000)
    assert r.frames[transitions.STEPS // 2].tobytes() not in (old.convert("RGB").tobytes(), new.convert("RGB").tobytes())


@pytest.mark.parametrize("kind", DRAWN)
def test_transition_stays_small_enough_to_upload_quickly(kind):
    data, is_gif = render.encode(transitions.build(kind, *_pages()))
    assert is_gif and len(data) < 8_000


def test_pick():
    assert transitions.pick("none") is None
    assert transitions.pick("something_old") is None
    assert transitions.pick(None) is None
    assert transitions.pick("wipe") == "wipe"
    assert transitions.pick("random", random.Random(1)) in DRAWN


def test_frame_at_follows_the_loop():
    frames = [Image.new("RGB", (W, H), (i, 0, 0)) for i in range(3)]
    r = render.Rendered(frames, [100, 100, 100])
    assert frame_at(r, 0) is frames[0]
    assert frame_at(r, 150) is frames[1]
    assert frame_at(r, 350) is frames[0]
    assert frame_at(render.Rendered(frames[:1]), 5000) is frames[0]
