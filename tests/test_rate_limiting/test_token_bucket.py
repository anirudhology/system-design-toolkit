import pytest
import time
import threading

from src.rate_limiting.token_bucket import TokenBucket


class TestTokenBucket:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.default_bucket = TokenBucket(capacity=10, fill_rate=1)

    def test_init(self):
        tb = TokenBucket(capacity=5, fill_rate=0.5)
        assert tb.capacity == 5
        assert tb.fill_rate == 0.5
        assert tb.tokens == 5
        assert isinstance(tb.last_fill_time, float)
        assert isinstance(tb.tokens, int)
        assert isinstance(tb.capacity, int)
        assert isinstance(tb.fill_rate, float)

    def test_init_invalid_fill_rate(self):
        with pytest.raises(ValueError):
            TokenBucket(capacity=5, fill_rate=-1)

    def test_get_available_tokens(self):
        assert self.default_bucket.get_available_tokens() == 10

    def test_consume_success(self):
        assert self.default_bucket.consume(5) is True
        assert self.default_bucket.tokens == 5

    def test_consume_failure(self):
        assert self.default_bucket.consume(11) is False
        assert self.default_bucket.tokens == 10

    def test_consume_exact(self):
        assert self.default_bucket.consume(10) is True
        assert self.default_bucket.tokens == 0

    def test_consume_invalid(self):
        with pytest.raises(ValueError):
            self.default_bucket.consume(-1)

    def test_add_tokens(self):
        tb = TokenBucket(capacity=10, fill_rate=1)
        time.sleep(2)  # Wait for 2 seconds
        tb.add_tokens()
        assert 10 <= tb.tokens <= 12  # Allow for small timing discrepancies

    def test_add_tokens_overflow(self):
        tb = TokenBucket(capacity=10, fill_rate=5)
        time.sleep(3)  # Wait for 3 seconds
        tb.add_tokens()
        assert tb.tokens == 10  # Should not exceed capacity

    def test_add_tokens_no_change(self):
        original_time = self.default_bucket.last_fill_time
        self.default_bucket.add_tokens()
        assert self.default_bucket.tokens == 10
        assert self.default_bucket.last_fill_time == original_time

    def test_concurrent_access(self):
        tb = TokenBucket(capacity=100, fill_rate=10)

        def consume():
            for _ in range(50):
                tb.consume(1)

        threads = [threading.Thread(target=consume) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert 0 <= tb.tokens <= 100

    def test_long_period_without_access(self):
        time.sleep(5)  # Wait for 5 seconds
        assert self.default_bucket.get_available_tokens() == 10

    def test_consume_and_refill(self):
        assert self.default_bucket.consume(5) is True
        time.sleep(3)
        assert 7 <= self.default_bucket.get_available_tokens() <= 8  # Allow for small timing discrepancies

    def test_rapid_consume(self):
        for _ in range(10):
            assert self.default_bucket.consume(1) is True
        assert self.default_bucket.consume(1) is False
