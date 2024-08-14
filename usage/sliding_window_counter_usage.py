import time

from src.rate_limiting.sliding_window_counter import SlidingWindowCounter


def simulate_requests(counter, num_requests, delay=0):
    """Simulate a series of requests and print the results."""
    allowed = 0
    denied = 0
    for i in range(num_requests):
        if counter.allow_request():
            print(f"Request {i + 1}: Allowed")
            allowed += 1
        else:
            print(f"Request {i + 1}: Denied (Rate limit exceeded)")
            denied += 1
        if delay > 0:
            time.sleep(delay)
    print(f"Allowed: {allowed}, Denied: {denied}")
    print("Current stats:", counter.get_stats())


def main():
    print("Scenario 1: Basic rate limiting")
    # Allow 5 requests per second
    counter = SlidingWindowCounter(max_allowed_requests=5, window_size=1.0)
    simulate_requests(counter, 10)

    print("\nScenario 2: Requests over time")
    counter = SlidingWindowCounter(max_allowed_requests=5, window_size=1.0)
    for i in range(15):
        if i % 5 == 0 and i > 0:
            print(f"Waiting for 1 second... (Current time: {time.time():.2f})")
            time.sleep(1)
        if counter.allow_request():
            print(f"Request {i + 1}: Allowed")
        else:
            print(f"Request {i + 1}: Denied")
    print("Final stats:", counter.get_stats())

    print("\nScenario 3: Reset functionality")
    counter = SlidingWindowCounter(max_allowed_requests=5, window_size=1.0)
    simulate_requests(counter, 5)
    print("Resetting counter...")
    counter.reset()
    print("After reset:", counter.get_stats())
    simulate_requests(counter, 5)


if __name__ == "__main__":
    main()
