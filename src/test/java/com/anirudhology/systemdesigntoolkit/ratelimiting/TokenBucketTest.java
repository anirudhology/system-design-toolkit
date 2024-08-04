package com.anirudhology.systemdesigntoolkit.ratelimiting;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class TokenBucketTest {

    private static final long REFILL_TOKENS = 5; // Tokens added per second
    private static final long REFILL_TIME_MS = 1000; // Refill interval in milliseconds
    private static final long CAPACITY = 20; // Bucket capacity

    private TokenBucket tokenBucket;

    @BeforeEach
    public void setUp() {
        tokenBucket = new TokenBucket(CAPACITY, REFILL_TOKENS, REFILL_TIME_MS);
    }

    @Test
    public void testAllowRequestsWithinCapacity() {
        for (int i = 0; i < CAPACITY; i++) {
            assertTrue(tokenBucket.isRequestAllowed(1), "Request should be allowed");
        }
    }

    @Test
    public void testDenyRequestsExceedingCapacity() {
        for (int i = 0; i < CAPACITY; i++) {
            assertTrue(tokenBucket.isRequestAllowed(1), "Request should be allowed");
        }
        // The next request should be denied
        assertFalse(tokenBucket.isRequestAllowed(1), "Request should be denied");
    }

    @Test
    public void testRefillTokensAfterInterval() throws InterruptedException {
        for (int i = 0; i < CAPACITY; i++) {
            assertTrue(tokenBucket.isRequestAllowed(1), "Request should be allowed");
        }
        // The next request should be denied
        assertFalse(tokenBucket.isRequestAllowed(1), "Request should be denied");

        // Wait for tokens to be refilled
        Thread.sleep(REFILL_TIME_MS * 2);

        // After refilling, requests should be allowed again
        assertTrue(tokenBucket.isRequestAllowed(1), "Request should be allowed after refill");
    }

    @Test
    public void testBurstRequestsWithinCapacity() {
        assertTrue(tokenBucket.isRequestAllowed(CAPACITY), "Burst request within capacity should be allowed");
        // The next request should be denied
        assertFalse(tokenBucket.isRequestAllowed(1), "Request should be denied after burst");
    }

    @Test
    public void testMultipleTokensRequiredPerRequest() {
        long tokensRequired = 5;
        for (int i = 0; i < CAPACITY / tokensRequired; i++) {
            assertTrue(tokenBucket.isRequestAllowed(tokensRequired), "Request should be allowed");
        }
        // The next request should be denied
        assertFalse(tokenBucket.isRequestAllowed(tokensRequired), "Request should be denied");
    }
}