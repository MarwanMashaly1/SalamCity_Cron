import time

class RateLimiter:
    def __init__(self, rate, burst):
        self.rate = rate  # Requests per second
        self.burst = burst  # Maximum burst size
        self.tokens = burst
        self.last_time = time.monotonic()

    def __enter__(self):
        self.wait()
        self.tokens -= 1
        if self.tokens < 0:
            raise Exception("Rate limit exceeded")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def wait(self):
        now = time.monotonic()
        time_passed = now - self.last_time
        self.tokens += time_passed * self.rate
        self.tokens = min(self.tokens, self.burst)
        self.last_time = now
        if self.tokens < 1:
            delay = 1 / self.rate
            time.sleep(delay)
            self.tokens += delay * self.rate  # Replenish after sleep
