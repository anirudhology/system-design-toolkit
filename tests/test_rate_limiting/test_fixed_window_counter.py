import pytest
import time

from src.rate_limiting.fixed_window_counter import FixedWindowCounter


class TestFixedWindowCounter:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Setup fixture for all tests
        self.fixed_window_counter = FixedWindowCounter(max_allowed_requests=5, window_size=10)

    def test_allow_request_within_window(self):
        # Allow 5 requests within the same window
        for _ in range(5):
            assert self.fixed_window_counter.allow_request() is True
        # 6th request should be rejected
        assert self.fixed_window_counter.allow_request() is False

    def test_allow_request_new_window(self):
        # Allow 5 requests within the first window
        for _ in range(5):
            assert self.fixed_window_counter.allow_request() is True
        # 6th request should be rejected
        assert self.fixed_window_counter.allow_request() is False

        # Wait for the window to reset
        time.sleep(10)

        # After window reset, requests should be allowed again
        assert self.fixed_window_counter.allow_request() is True

    def test_get_window_status(self):
        # Allow 3 requests
        for _ in range(3):
            self.fixed_window_counter.allow_request()

        # Check window status
        status = self.fixed_window_counter.get_window_status()
        assert status['requests_made'] == 3
        assert status['time_remaining_in_window'] > 0

    def test_reset_window(self):
        # Allow 3 requests
        for _ in range(3):
            self.fixed_window_counter.allow_request()

        # Reset the window
        self.fixed_window_counter.reset_window()

        # After reset, request count should be zero
        assert self.fixed_window_counter.get_window_status()['requests_made'] == 0

    def test_get_remaining_requests(self):
        # Allow 3 requests
        for _ in range(3):
            self.fixed_window_counter.allow_request()

        # Check remaining requests
        assert self.fixed_window_counter.get_remaining_requests() == 2

    def test_invalid_initialization(self):
        # Test invalid initialization with negative values
        with pytest.raises(ValueError):
            FixedWindowCounter(max_allowed_requests=-1, window_size=10)

        with pytest.raises(ValueError):
            FixedWindowCounter(max_allowed_requests=5, window_size=-10)
