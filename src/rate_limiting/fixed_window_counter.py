import time
from threading import Lock


class FixedWindowCounter:
    def __init__(self, max_allowed_requests: int, window_size: float):
        """
        Initialize fixed window rate limiter

        :param max_allowed_requests: maximum number of allowed requests per window
        :param window_size: size of the time window in seconds
        """
        if max_allowed_requests <= 0 or window_size <= 0:
            raise ValueError("max_allowed_requests and window_size must be positive")

        self.max_allowed_requests: int = max_allowed_requests
        self.window_size: float = window_size

        self.current_request_count = 0  # Current request count within the window
        self.window_start_time = time.monotonic()  # Start time of the current window

        self.lock: Lock = Lock()  # Lock for thread safety

    def allow_request(self) -> bool:
        """
        Determines if a request is allowed or not

        :return: True, if request is allowed, False otherwise
        """
        with self.lock:
            current_time = time.monotonic()
            # Check if we are still within the current window
            if current_time - self.window_start_time < self.window_size:
                # Check if we have not exhausted our requests for the current window
                if self.current_request_count < self.max_allowed_requests:
                    self.current_request_count += 1
                    return True
                else:
                    return False
            else:
                # Reset the counter and start a new window
                self.window_start_time = current_time
                self.current_request_count = 1
                return True

    def get_window_status(self) -> dict[str, int]:
        """
        Get the current status of window, useful for debugging or monitoring

        :return: A dictionary with the current request count and time remaining in the window.
        """
        with self.lock:
            current_time = time.monotonic()
            time_remaining = max(0, int(self.window_size - (current_time - self.window_start_time)))
            return {
                'requests_made': self.current_request_count,
                'time_remaining_in_window': time_remaining
            }

    def reset_window(self) -> None:
        """
        Resets the window to its initial configuration
        """
        with self.lock:
            self.window_start_time = time.monotonic()
            self.current_request_count = 0

    def get_remaining_requests(self) -> int:
        """
        Returns remaining requests in the window

        :return: count of remaining requests
        """
        with self.lock:
            return max(0, self.max_allowed_requests - self.current_request_count)
