"""测试公共配置。"""

import pytest


@pytest.fixture
def mock_event_bus():
    """Mock 事件总线（不实际分发事件）。"""

    class _MockEventBus:
        def __init__(self):
            self.published = []

        def publish(self, event):
            self.published.append(event)

        def publish_all(self, events):
            self.published.extend(events)

        def subscribe(self, event_type, handler):
            pass

    return _MockEventBus()
