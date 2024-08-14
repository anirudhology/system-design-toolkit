import time

from src.rate_limiting.sliding_window_counter import SlidingWindowCounter


def simulate_requests(counter: SlidingWindowCounter, num_requests: int, delay: float = 0):
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
    print("Current status:", counter.get_window_status())


def main():
    print("Scenario 1: Basic rate limiting")
    # Allow 5 requests per second
    counter = SlidingWindowCounter(max_allowed_requests=5, window_size=1.0)
    simulate_requests(counter, 10)

    print("\nScenario 2: Requests over time (demonstrating sliding window effect)")
    counter = SlidingWindowCounter(max_allowed_requests=5, window_size=1.0)
    for i in range(15):
        if i % 5 == 0 and i > 0:
            print(f"Waiting for 0.5 seconds... (Current time: {time.time():.2f})")
            time.sleep(0.5)
        if counter.allow_request():
            print(f"Request {i + 1}: Allowed")
        else:
            print(f"Request {i + 1}: Denied")
        print("Status:", counter.get_window_status())

    print("\nScenario 3: Reset functionality")
    counter = SlidingWindowCounter(max_allowed_requests=5, window_size=1.0)
    simulate_requests(counter, 5)
    print("Resetting counter...")
    counter.reset()
    print("After reset:", counter.get_window_status())
    simulate_requests(counter, 5)

    print("\nScenario 4: High-frequency requests")
    counter = SlidingWindowCounter(max_allowed_requests=100, window_size=1.0)
    simulate_requests(counter, 150, delay=0.01)

    print("\nScenario 5: Demonstrating sliding window effect")
    counter = SlidingWindowCounter(max_allowed_requests=10, window_size=1.0)
    simulate_requests(counter, 10)  # Fill the current window
    time.sleep(0.5)  # Wait for half a window
    print("After waiting 0.5 seconds:")
    simulate_requests(counter, 5)  # Should allow fewer requests due to sliding window effect


if __name__ == "__main__":
    main()
