import time

from src.rate_limiting.token_bucket import TokenBucket


def simulate_api_calls(rate_limiter: TokenBucket, num_calls: int, delay: float = 0):
    """Simulate API calls and print the results."""
    allowed = 0
    denied = 0
    for i in range(num_calls):
        if rate_limiter.consume(1):
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
    bucket = TokenBucket(capacity=5, fill_rate=5)
    simulate_api_calls(bucket, 10)

    print("\nScenario 2: Burst traffic handling")
    # Allow bursts of up to 10 requests, but maintain 5 per second long-term rate
    bucket = TokenBucket(capacity=10, fill_rate=5)
    simulate_api_calls(bucket, 15)

    print("\nScenario 3: Gradual token refill")
    bucket = TokenBucket(capacity=5, fill_rate=1)  # 1 token per second
    for i in range(10):
        if bucket.consume(1):
            print(f"Second {i}: Request allowed. Tokens left: {bucket.get_available_tokens()}")
        else:
            print(f"Second {i}: Request denied. Tokens left: {bucket.get_available_tokens()}")
        time.sleep(1)

    print("\nScenario 4: High-volume traffic simulation")
    bucket = TokenBucket(capacity=100, fill_rate=10)  # 10 requests per second, up to 100 burst
    simulate_api_calls(bucket, 200, delay=0.05)  # 200 requests with 50ms between each

    print("\nScenario 5: Multiple token consumption")
    bucket = TokenBucket(capacity=10, fill_rate=2)  # 2 tokens per second, up to 10
    for i in range(5):
        tokens_to_consume = i + 1
        if bucket.consume(tokens_to_consume):
            print(f"Consumed {tokens_to_consume} tokens. Tokens left: {bucket.get_available_tokens()}")
        else:
            print(f"Failed to consume {tokens_to_consume} tokens. Tokens available: {bucket.get_available_tokens()}")
        time.sleep(1)


if __name__ == '__main__':
    main()
