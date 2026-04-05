"""Tests for EventBus."""
from __future__ import annotations
from pykworldsim.core.events import EventBus


def test_emit_fires_handler():
    bus = EventBus()
    received = []
    bus.subscribe("test", lambda d: received.append(d))
    bus.emit("test", {"value": 42})
    assert received == [{"value": 42}]

def test_subscribe_multiple_handlers():
    bus = EventBus()
    a, b = [], []
    bus.subscribe("ev", lambda d: a.append(1))
    bus.subscribe("ev", lambda d: b.append(2))
    bus.emit("ev")
    assert a and b

def test_emit_no_handlers_is_safe():
    bus = EventBus()
    bus.emit("nonexistent", {"x": 1})  # must not raise

def test_unsubscribe():
    bus = EventBus()
    called = []
    h = lambda d: called.append(1)
    bus.subscribe("ev", h)
    bus.unsubscribe("ev", h)
    bus.emit("ev")
    assert called == []

def test_deferred_not_fired_until_flush():
    bus = EventBus()
    received = []
    bus.subscribe("late", lambda d: received.append(d))
    bus.emit_deferred("late", {"x": 1})
    assert received == []
    bus.flush()
    assert received == [{"x": 1}]

def test_flush_clears_queue():
    bus = EventBus()
    received = []
    bus.subscribe("ev", lambda d: received.append(1))
    bus.emit_deferred("ev")
    bus.flush()
    bus.flush()  # second flush must not re-fire
    assert len(received) == 1

def test_subscriber_count():
    bus = EventBus()
    bus.subscribe("ev", lambda d: None)
    bus.subscribe("ev", lambda d: None)
    assert bus.subscriber_count("ev") == 2

def test_clear():
    bus = EventBus()
    called = []
    bus.subscribe("ev", lambda d: called.append(1))
    bus.emit_deferred("ev")
    bus.clear()
    bus.flush()
    assert called == []
