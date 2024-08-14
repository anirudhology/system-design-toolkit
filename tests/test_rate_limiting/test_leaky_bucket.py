import pytest
import time

from src.rate_limiting.leaky_bucket import LeakyBucket


class TestLeakyBucket:

    def test_init(self):
        lb = LeakyBucket(capacity=10, leak_rate=1)
        assert lb.capacity == 10
        assert lb.leak_rate == 1
        assert lb.tokens == 0
        assert isinstance(lb.last_leak_time, float)

    def test_init_invalid_params(self):
        with pytest.raises(ValueError):
            LeakyBucket(capacity=0, leak_rate=1)
        with pytest.raises(ValueError):
            LeakyBucket(capacity=10, leak_rate=0)
        with pytest.raises(ValueError):
            LeakyBucket(capacity=-1, leak_rate=-1)

    def test_get_available_tokens_empty(self):
        lb = LeakyBucket(capacity=10, leak_rate=1)
        assert lb.get_available_tokens() == 0

    def test_get_available_tokens_with_tokens(self):
        lb = LeakyBucket(capacity=10, leak_rate=1)
        lb.add_tokens(5)
        assert lb.get_available_tokens() == 5

    def test_add_tokens_success(self):
        lb = LeakyBucket(capacity=10, leak_rate=1)
        assert lb.add_tokens(5) == True
        assert lb.tokens == 5

    def test_add_tokens_failure(self):
        lb = LeakyBucket(capacity=10, leak_rate=1)
        assert lb.add_tokens(11) == False
        assert lb.tokens == 0

    def test_add_tokens_exact_capacity(self):
        lb = LeakyBucket(capacity=10, leak_rate=1)
        assert lb.add_tokens(10) == True
        assert lb.tokens == 10

    def test_add_negative_tokens(self):
        lb = LeakyBucket(capacity=10, leak_rate=1)
        with pytest.raises(ValueError):
            lb.add_tokens(-1)

    def test_leak(self):
        lb = LeakyBucket(capacity=10, leak_rate=1)
        lb.add_tokens(10)
        time.sleep(2)  # Wait for 2 seconds
        assert 7 <= lb.get_available_tokens() <= 8  # Allow for small timing discrepancies

    def test_leak_to_zero(self):
        lb = LeakyBucket(capacity=10, leak_rate=10)
        lb.add_tokens(10)
        time.sleep(1.1)  # Wait for slightly more than 1 second
        assert lb.get_available_tokens() == 0

    def test_add_tokens_after_leak(self):
        lb = LeakyBucket(capacity=10, leak_rate=1)
        lb.add_tokens(10)
        time.sleep(2)  # Wait for 2 seconds
        assert lb.add_tokens(3) is False
        assert 8 <= lb.get_available_tokens() <= 11  # Allow for small timing discrepancies

    def test_rapid_add_tokens(self):
        lb = LeakyBucket(capacity=10, leak_rate=1)
        for _ in range(10):
            assert lb.add_tokens(1) is True
        assert lb.add_tokens(1) is False

    @pytest.mark.parametrize("capacity,leak_rate,sleep_time,expected_min,expected_max", [
        (10, 1, 2, 7, 8),
        (20, 2, 3, 13, 14),
        (5, 0.5, 4, 2, 3),
    ])
    def test_various_rates(self, capacity, leak_rate, sleep_time, expected_min, expected_max):
        lb = LeakyBucket(capacity=capacity, leak_rate=leak_rate)
        lb.add_tokens(lb.capacity)  # Fill the bucket
        time.sleep(sleep_time)
        assert expected_min <= lb.get_available_tokens() <= expected_max
