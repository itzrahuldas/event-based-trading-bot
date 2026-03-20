import time
import threading
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RateLimiter:
    def __init__(self, max_calls: int, period: int):
        """
        Token Bucket Rate Limiter.
        :param max_calls: Number of calls allowed in 'period' seconds.
        :param period: Time window in seconds.
        """
        self.max_calls = max_calls
        self.period = period
        self.tokens = max_calls
        self.last_refill = time.time()
        self.lock = threading.Lock()
        
    def acquire(self):
        """
        Blocks until a token is available.
        Thread-safe using Token Bucket algorithm.
        """
        while True:
            with self.lock:
                now = time.time()
                # Refill tokens based on time elapsed
                elapsed = now - self.last_refill
                if elapsed > self.period:
                    self.tokens = self.max_calls
                    self.last_refill = now
                
                if self.tokens > 0:
                    self.tokens -= 1
                    return
                else:
                    # Calculate time until next period reset
                    wait_time = self.period - elapsed
            
            # Sleep outside the lock to allow other threads to potentially release/check
            if wait_time > 0:
                time.sleep(wait_time + 0.01) # Small jitter
