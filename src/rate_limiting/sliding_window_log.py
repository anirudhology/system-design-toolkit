import time
from collections import deque
from threading import Lock


class SlidingWindowLog:
    def __init__(self, max_allowed_requests: int, window_size: float):
        """
        Initialize Sliding Window Log
        :param max_allowed_requests: maximum allowed request for a window
        :param window_size: size of the time window
        """
        if max_allowed_requests <= 0 or window_size <= 0:
            raise ValueError("Max allowed requests and window size should be positive")

        self.max_allowed_requests: int = max_allowed_requests
        self.window_size: float = window_size

        self.request_timestamps: deque = deque()  # Timestamps of the requests received
        self.current_request_count: int = 0  # Current count of requests in the window
        self.last_request_time: float = time.monotonic()  # Timestamp of the last received request

        self.lock: Lock = Lock()

    def allow_request(self) -> bool:
        """
        Determines if a new request is allowed

        :return: True, if the request is allowed, False otherwise
        """
        with self.lock:
            current_time = time.monotonic()
            self.__remove_old_requests(current_time)

            if self.current_request_count < self.max_allowed_requests:
                self.request_timestamps.append(current_time)
                self.current_request_count += 1
                self.last_request_time = current_time
                return True
            return False

    def get_stats(self) -> dict:
        """
        Get current statistics about the sliding window

        :return: A dictionary containing current stats
        """
        with self.lock:
            current_time = time.monotonic()
            self.__remove_old_requests(current_time)

            return {
                'current_request_count': self.current_request_count,
                'allowed_requests': self.max_allowed_requests,
                'window_size': self.window_size,
                'last_request_time': current_time - self.last_request_time
            }

    def reset(self) -> None:
        """
        Reset the rate limiter to its initial stats
        """
        with self.lock:
            self.request_timestamps.clear()
            self.current_request_count = 0
            self.last_request_time = time.monotonic()

    def __remove_old_requests(self, current_time):
        """
        Removes request that are outside the current rolling window

        :param current_time: the current timestamp
        """
        window_start_time = current_time - self.window_size
        while self.request_timestamps and self.request_timestamps[0] <= window_start_time:
            self.request_timestamps.popleft()
            self.current_request_count -= 1
