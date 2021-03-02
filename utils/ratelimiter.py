from datetime import datetime


class RateLimiter:
    def __init__(self, rate: int):
        self.rate = rate
        self.timestamps = {}

    async def check_rate(self, webhook: str, token: bool = False):
        if token:
            return True
        else:
            if webhook not in self.timestamps:
                self.timestamps[webhook] = datetime.now()
                return True
            else:
                time_passed = (
                    datetime.now() - self.timestamps[webhook]
                ).total_seconds()
                if time_passed >= self.rate:
                    self.timestamps[webhook] = datetime.now()
                    return True
                else:
                    return False
