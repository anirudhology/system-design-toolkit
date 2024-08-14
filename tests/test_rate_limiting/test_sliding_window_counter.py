import pytest
import time

from src.rate_limiting.sliding_window_counter import SlidingWindowCounter


class TestSlidingWindowCounter:

    def test_init(self):
        swc = SlidingWindowCounter(max_allowed_requests=10, window_size=1.0)
        assert swc.max_allowed_requests == 10
        assert swc.window_size == 1.0
        assert swc.current_request_count == 0
        assert swc.previous_request_count == 0

    def test_init_invalid_params(self):
        with pytest.raises(ValueError):
            SlidingWindowCounter(max_allowed_requests=0, window_size=1.0)
        with pytest.raises(ValueError):
            SlidingWindowCounter(max_allowed_requests=10, window_size=0)
        with pytest.raises(ValueError):
            SlidingWindowCounter(max_allowed_requests=-1, window_size=-1)

    def test_allow_request_within_limit(self):
        swc = SlidingWindowCounter(max_allowed_requests=2, window_size=1.0)
        assert swc.allow_request() is True
        assert swc.allow_request() is True
        assert swc.current_request_count == 2

    def test_allow_request_exceeds_limit(self):
        swc = SlidingWindowCounter(max_allowed_requests=2, window_size=1.0)
        assert swc.allow_request() is True
        assert swc.allow_request() is True
        assert swc.allow_request() is False
        assert swc.current_request_count == 2

    def test_allow_request_new_window(self):
        swc = SlidingWindowCounter(max_allowed_requests=2, window_size=0.1)
        assert swc.allow_request() is True
        assert swc.allow_request() is True
        time.sleep(0.11)  # Wait for new window
        assert swc.allow_request() is True
        assert swc.current_request_count == 1
        assert swc.previous_request_count == 2

    def test_allow_request_sliding_window_effect(self):
        swc = SlidingWindowCounter(max_allowed_requests=3, window_size=0.1)
        assert swc.allow_request() is True
        assert swc.allow_request() is True
        assert swc.allow_request() is True
        time.sleep(0.05)  # Wait for half window
        assert swc.allow_request() is False  # Should be denied due to sliding window effect

    def test_get_window_status(self):
        swc = SlidingWindowCounter(max_allowed_requests=10, window_size=1.0)
        swc.allow_request()
        status = swc.get_window_status()
        assert 'current_window' in status
        assert status['current_request_count'] == 1
        assert status['previous_request_count'] == 0
        assert 0 <= status['time_remaining_in_window'] <= 1.0

    def test_reset(self):
        swc = SlidingWindowCounter(max_allowed_requests=10, window_size=1.0)
        swc.allow_request()
        swc.allow_request()
        swc.reset()
        assert swc.current_request_count == 0
        assert swc.previous_request_count == 0

    def test_thread_safety(self):
        import threading
        swc = SlidingWindowCounter(max_allowed_requests=1000, window_size=1.0)

        def make_requests():
            for _ in range(100):
                swc.allow_request()

        threads = [threading.Thread(target=make_requests) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert swc.current_request_count + swc.previous_request_count <= 1000
