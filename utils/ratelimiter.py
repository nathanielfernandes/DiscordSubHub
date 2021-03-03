from datetime import datetime


class RateLimiter:
    """Handles rate limiting.
    """

    def __init__(self, rate: int):
        self.rate = rate
        self.timestamps = {}

    async def check_rate(self, webhook: str, token: bool = False):
        if token:
            return False, str(0)
        else:
            if webhook not in self.timestamps:
                self.timestamps[webhook] = datetime.now()
                return False, str(0)
            else:
                time_passed = (
                    datetime.now() - self.timestamps[webhook]
                ).total_seconds()
                if time_passed >= self.rate:
                    self.timestamps[webhook] = datetime.now()
                    return False, str(0)
                else:
                    return True, f"{self.rate-time_passed:0.1f}"
