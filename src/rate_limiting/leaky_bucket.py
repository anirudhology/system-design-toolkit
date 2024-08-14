import time
from threading import Lock


class LeakyBucket:
    def __init__(self, capacity: int, leak_rate: float):
        """
        Initialize the leaky bucket

        :param capacity: Maximum number of request that can be processed
        :param leak_rate: Number of tokens that leak per unit of time
        """
        if capacity <= 0 or leak_rate <= 0:
            raise ValueError("Capacity or leak rate should be positive")

        self.capacity: int = capacity
        self.leak_rate: float = leak_rate

        self.tokens: int = 0  # Current number of tokens in the bucket
        self.last_leak_time: float = time.monotonic()  # Last time we checked the bucket

        # Lock for thread safety
        self.lock: Lock = Lock()

    def get_available_tokens(self) -> int:
        """
        Get current water level (number of tokens available) in the bucket
        :return: available tokens
        """
        with self.lock:
            self.leak()  # Ensure that the number of tokens is up-to-date
            return self.tokens

    def add_tokens(self, amount: int) -> bool:
        """
        Add tokens to the bucket

        :param amount: amount of tokens to be added (number of incoming requests)
        :return: True, if request was added successfully, False otherwise
        """
        if amount < 0:
            raise ValueError("Cannot add negative requests")

        with self.lock:
            self.leak()  # First, leak tokens based on the time passed

            if self.tokens + amount <= self.capacity:
                self.tokens += amount
                return True

            return False

    def leak(self):
        """
        Simulate the leaking of the bucket based on the elapsed time
        This method is not thread-safe and should be called within a lock
        """
        current_time = time.monotonic()
        time_elapsed = current_time - self.last_leak_time
        leaked_tokens = time_elapsed * self.leak_rate  # Number of requests that have been processed

        self.tokens = max(0, round(self.tokens - leaked_tokens))
        self.last_leak_time = current_time
