from datetime import time

from pixel_clock import schedule as s


def test_parse_time():
    assert s.parse_time("06:00:00") == time(6, 0)
    assert s.parse_time("17:30") == time(17, 30)
    assert s.parse_time(time(8, 15)) == time(8, 15)
    for bad in (None, "", "abc", "25:00", "6", 7):
        assert s.parse_time(bad) is None


def test_format_time_is_read_back():
    assert s.format_time(time(6, 5)) == "06:05:00"
    assert s.parse_time(s.format_time(time(22, 30))) == time(22, 30)


def test_window_during_the_day():
    assert s.in_window(time(6, 0), "06:00:00", "17:00:00")
    assert s.in_window(time(16, 59), "06:00:00", "17:00:00")
    assert not s.in_window(time(17, 0), "06:00:00", "17:00:00")
    assert not s.in_window(time(5, 59), "06:00:00", "17:00:00")


def test_window_past_midnight():
    assert s.in_window(time(23, 0), "22:00", "06:00")
    assert s.in_window(time(2, 0), "22:00", "06:00")
    assert not s.in_window(time(6, 0), "22:00", "06:00")
    assert not s.in_window(time(12, 0), "22:00", "06:00")


def test_open_windows():
    assert s.in_window(time(3, 0), None, None)
    assert s.in_window(time(3, 0), "", "")
    assert s.in_window(time(18, 0), "17:00", None)
    assert not s.in_window(time(16, 0), "17:00", None)
    assert s.in_window(time(9, 0), None, "12:00")
    assert not s.in_window(time(12, 0), None, "12:00")
    assert s.in_window(time(9, 0), "08:00", "08:00")


def test_schedule_morning_and_evening():
    slots = [("06:00:00", "09:00:00"), (None, None), ("17:00:00", "22:00:00")]
    assert s.in_schedule(time(6, 0), slots)
    assert s.in_schedule(time(21, 59), slots)
    assert not s.in_schedule(time(9, 0), slots)
    assert not s.in_schedule(time(12, 0), slots)
    assert not s.in_schedule(time(22, 0), slots)


def test_schedule_past_midnight():
    assert s.in_schedule(time(1, 0), [("22:00", "02:00")])
    assert not s.in_schedule(time(3, 0), [("22:00", "02:00")])


def test_unused_slots_mean_always_on():
    assert s.in_schedule(time(3, 0), [])
    assert s.in_schedule(time(3, 0), [(None, None), ("", "")])
    assert s.in_schedule(time(3, 0), [("08:00", "08:00")])  # same time: slot not used
    assert s.in_schedule(time(3, 0), [("08:00", None)])  # incomplete: slot not used
    assert not s.in_schedule(time(3, 0), [("08:00", "08:00"), ("06:00", "09:00")])
