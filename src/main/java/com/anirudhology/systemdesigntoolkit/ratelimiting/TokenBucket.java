package com.anirudhology.systemdesigntoolkit.ratelimiting;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class TokenBucket {

    private static final long DEFAULT_CAPACITY = 1 << 4;
    // The maximum number of tokens a bucket can hold
    private final long capacity;
    // The number of tokens to be added to the bucket at each refill interval
    private final long refillTokens;
    // The time interval after which the tokens will be refilled
    private final long refillTimeMilliseconds;
    // Current number of tokens available in the bucket
    private long availableTokens;
    // Timestamp at which the tokens were last refilled
    private long lastTokenRefillTimeMilliseconds;
    // Lock to ensure thread safety
    private final Lock lock;

    // Bucket with default capacity
    public TokenBucket(long refillTokens, long refillTimeMilliseconds) {
        this(DEFAULT_CAPACITY, refillTokens, refillTimeMilliseconds);
    }

    // Bucket with custom capacity
    public TokenBucket(long capacity, long refillTokens, long refillTimeMilliseconds) {
        this.capacity = capacity;
        this.refillTokens = refillTokens;
        this.refillTimeMilliseconds = refillTimeMilliseconds;
        this.availableTokens = capacity;
        this.lastTokenRefillTimeMilliseconds = System.currentTimeMillis();
        this.lock = new ReentrantLock();
    }

    public boolean isRequestAllowed(long tokensRequired) {
        // Acquire the lock
        lock.lock();
        try {
            refill();
            // Check if we have sufficient tokens to allow the request
            if (availableTokens >= tokensRequired) {
                availableTokens -= tokensRequired;
                return true;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }

    private void refill() {
        long currentTime = System.currentTimeMillis();
        long elapsedTime = currentTime - lastTokenRefillTimeMilliseconds;
        // Check if we need to add new tokens
        if (elapsedTime >= refillTimeMilliseconds) {
            long newTokens = (elapsedTime / refillTimeMilliseconds) * refillTokens;
            availableTokens = Math.min(capacity, newTokens + availableTokens);
            lastTokenRefillTimeMilliseconds = currentTime;
        }
    }
}
