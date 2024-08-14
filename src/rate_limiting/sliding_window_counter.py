import time
from threading import Lock


class SlidingWindowCounter:
    def __init__(self, max_allowed_requests: int, window_size: float):
        """
        Initializes Sliding Window Counter

        :param max_allowed_requests: number of allowed requests in a window
        :param window_size: size of the window
        """
        if max_allowed_requests <= 0 or window_size <= 0:
            raise ValueError("Max allowed requests and window size should be positive")

        self.max_allowed_requests: int = max_allowed_requests
        self.window_size: float = window_size

        self.current_window: int = int(time.monotonic() // window_size)  # Current window identifier
        self.current_request_count: int = 0  # Request count in the current window
        self.previous_request_count: int = 0  # Request count in the previous window

        self.lock: Lock = Lock()

    def allow_request(self) -> bool:
        """
        Determines if a request is allowed in the current window
        :return: True, if the request is allowed, False otherwise
        """
        with self.lock:
            current_time = time.monotonic()
            current_window = int(current_time // self.window_size)

            if current_window == self.current_window:
                # Same window, check if the request is allowed
                if self.current_request_count < self.max_allowed_requests:
                    self.current_request_count += 1
                    return True
                return False
            else:
                # Next window, shift counters
                time_elapsed_in_current_window = (current_time % self.window_size) / self.window_size
                previous_window_weight = 1 - time_elapsed_in_current_window

                # Sliding window effect: weighted combination of current and previous window counts
                allowed_count = (
                        self.current_request_count * (1 - previous_window_weight) +
                        self.previous_request_count * previous_window_weight
                )

                if allowed_count < self.max_allowed_requests:
                    self.previous_request_count = self.current_request_count
                    self.current_window = current_window
                    self.current_request_count = 1  # First request in new window
                    return True
                return False

    def get_window_status(self) -> dict[str, int]:
        """
        Get the current status of window, useful for debugging or monitoring

        :return: A dictionary with the current request count, previous window count, and time remaining in the window
        """
        with self.lock:
            current_time = time.monotonic()
            current_window = int(current_time // self.window_size)
            time_remaining = self.window_size - (current_time % self.window_size)

            return {
                'current_window': current_window,
                'current_request_count': self.current_request_count,
                'previous_request_count': self.previous_request_count,
                'time_remaining_in_window': time_remaining
            }

    def reset(self) -> None:
        """
        Resets the window to its initial configuration
        """
        with self.lock:
            self.current_window = int(time.monotonic() // self.window_size)
            self.current_request_count = 0
            self.previous_request_count = 0
