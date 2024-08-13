import time
from threading import Lock


class TokenBucket:
    def __init__(self, capacity: int, fill_rate: float):
        """
        Initialize the token bucket
        :param capacity: maximum number of tokens a bucket can hold
        :param fill_rate: number of tokens added per unit of time
        """
        if capacity <= 0 or fill_rate <= 0:
            raise ValueError("Capacity and fill rate must be a positive number")

        self.capacity: int = capacity
        self.fill_rate: float = fill_rate

        # Current token count
        self.tokens: int = capacity
        # Last time when the bucket was filled
        self.last_fill_time: float = time.monotonic()

        # Lock for thread safety
        self.lock: Lock = Lock()

    def get_available_tokens(self) -> int:
        """
        Get the current number of tokens in the bucket
        :return: tokens
        """
        with self.lock:
            self.add_tokens()  # Ensure that the token count is upto date
            return self.tokens

    def add_tokens(self):
        """
        Add tokens to the token bucket
        """
        # Get the current time
        current_time = time.monotonic()
        time_elapsed = current_time - self.last_fill_time
        new_tokens = time_elapsed * self.fill_rate

        if new_tokens > 0:
            self.tokens = min(self.capacity, round(new_tokens + self.tokens))
            self.last_fill_time = current_time

    def consume(self, tokens: int) -> bool:
        """
        Consume token from the bucket

        :param tokens: required tokens to consume
        :return: True, if tokens were consumed, False otherwise
        """
        if tokens < 0:
            raise ValueError("Cannot consume negative tokens")

        with self.lock:
            self.add_tokens()  # Refill tokens
            if tokens <= self.tokens:
                self.tokens -= tokens
                return True
            return False
