import time

from src.rate_limiting.leaky_bucket import LeakyBucket


def simulate_requests(bucket: LeakyBucket, num_requests: int, delay: float = 0):
    """Simulate a series of requests and print the results."""
    allowed = 0
    denied = 0
    for i in range(num_requests):
        if bucket.add_tokens(1):
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
    # Allow 5 requests per second
    bucket = LeakyBucket(capacity=5, leak_rate=5)
    simulate_requests(bucket, 10)

    print("\nScenario 2: Burst handling")
    # Allow bursts of up to 10 requests, but maintain 5 per second long-term rate
    bucket = LeakyBucket(capacity=10, leak_rate=5)
    simulate_requests(bucket, 15)

    print("\nScenario 3: Gradual token leak")
    bucket = LeakyBucket(capacity=5, leak_rate=1)  # 1 token per second
    for i in range(10):
        print(f"Second {i}: Tokens available: {bucket.get_available_tokens()}")
        if bucket.add_tokens(1):
            print("Request allowed")
        else:
            print("Request denied")
        time.sleep(1)

    print("\nScenario 4: High-volume traffic simulation")
    bucket = LeakyBucket(capacity=100, leak_rate=10)  # 10 requests per second, up to 100 burst
    simulate_requests(bucket, 200, delay=0.05)  # 200 requests with 50ms between each


if __name__ == "__main__":
    main()
