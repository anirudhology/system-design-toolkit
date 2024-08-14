import time

from src.rate_limiting.fixed_window_counter import FixedWindowCounter


def simulate_api_calls(rate_limiter: FixedWindowCounter, num_calls: int, delay: float = 0):
    """Simulate API calls and print the results."""
    allowed = 0
    denied = 0
    for i in range(num_calls):
        if rate_limiter.allow_request():
            print(f"Request {i + 1}: Allowed")
            allowed += 1
        else:
            print(f"Request {i + 1}: Denied (Rate limit exceeded)")
            denied += 1
        if delay > 0:
            time.sleep(delay)
    print(f"Allowed: {allowed}, Denied: {denied}")


def main():
    print("Scenario 1: Basic rate limiting")
    # Allow 5 requests per 10 seconds
    counter = FixedWindowCounter(max_allowed_requests=5, window_size=10)
    simulate_api_calls(counter, 10)

    print("\nScenario 2: Burst traffic handling")
    # Allow up to 10 requests per 10 seconds
    counter = FixedWindowCounter(max_allowed_requests=10, window_size=10)
    simulate_api_calls(counter, 15)

    print("\nScenario 3: Gradual window expiration")
    counter = FixedWindowCounter(max_allowed_requests=5, window_size=5)  # 5 requests per 5 seconds
    for i in range(10):
        if counter.allow_request():
            print(f"Second {i}: Request allowed. Remaining requests: {counter.get_remaining_requests()}")
        else:
            print(f"Second {i}: Request denied. Remaining requests: {counter.get_remaining_requests()}")
        time.sleep(1)

    print("\nScenario 4: High-volume traffic simulation")
    counter = FixedWindowCounter(max_allowed_requests=100, window_size=10)  # 100 requests per 10 seconds
    simulate_api_calls(counter, 200, delay=0.05)  # 200 requests with 50ms between each

    print("\nScenario 5: Reset window during active requests")
    counter = FixedWindowCounter(max_allowed_requests=5, window_size=5)  # 5 requests per 5 seconds
    for i in range(7):
        if counter.allow_request():
            print(f"Consumed 1 request. Remaining requests: {counter.get_remaining_requests()}")
        else:
            print(f"Request denied. Remaining requests: {counter.get_remaining_requests()}")
        time.sleep(1)

    # Resetting the window after some requests
    print("\nResetting the window")
    counter.reset_window()
    for i in range(3):
        if counter.allow_request():
            print(f"After reset - Consumed 1 request. Remaining requests: {counter.get_remaining_requests()}")
        else:
            print(f"After reset - Request denied. Remaining requests: {counter.get_remaining_requests()}")
        time.sleep(1)


if __name__ == '__main__':
    main()
