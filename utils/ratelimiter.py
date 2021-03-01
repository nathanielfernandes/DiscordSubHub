from datetime import datetime


class RateLimiter:
    def __init__(self, rate: int):
        self.rate = rate
        self.timestamps = {}

    async def check_rate(self, ip: str, token: bool):
        if not token:
            if ip not in self.timestamps:
                self.timestamps[ip] = datetime.now()
                return True
            else:
                time_passed = (datetime.now() - self.timestamps[ip]).total_seconds()
                if time_passed >= self.rate:
                    self.timestamps[ip] = datetime.now()
                    return True
                else:
                    return False
        else:
            return True

