import asyncio

class RateLimiter:

    def __init__(self, rate, burst):
        self.rate = rate  # Requests per second
        self.burst = burst  # Maximum burst size
        self.tokens = burst
        self.last_time = None

    def __enter__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.wait())
        self.tokens -= 1
        if self.tokens < 0:
            raise Exception("Rate limit exceeded")
        
    def __exit__(self, exc_type, exc_value, traceback):
        pass


    async def wait(self):
        if self.last_time is None:
            self.last_time = asyncio.get_event_loop().time()

        now = asyncio.get_event_loop().time()
        time_passed = now - self.last_time

        self.tokens += time_passed * self.rate
        self.tokens = min(self.tokens, self.burst)
        self.last_time = now

        if self.tokens < 1:
            delay = 1 / self.rate
            await asyncio.sleep(delay)
            self.tokens += 1
