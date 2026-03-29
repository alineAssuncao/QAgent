import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class RateLimitConfig:
    max_requests: int = 10
    window_seconds: int = 60


@dataclass
class UserRateLimit:
    requests: list = field(default_factory=list)
    blocked_until: Optional[float] = None


class RateLimiter:
    def __init__(self, config: RateLimitConfig = None) -> None:
        self.config = config or RateLimitConfig()
        self._user_limits: Dict[int, UserRateLimit] = defaultdict(UserRateLimit)

    def is_allowed(self, user_id: int) -> bool:
        now = time.time()
        user_limit = self._user_limits[user_id]

        if user_limit.blocked_until and now < user_limit.blocked_until:
            return False

        user_limit.requests = [
            t for t in user_limit.requests if now - t < self.config.window_seconds
        ]

        if len(user_limit.requests) >= self.config.max_requests:
            user_limit.blocked_until = now + self.config.window_seconds
            user_limit.requests.clear()
            logging.warning(f"Usuário {user_id} bloqueado por rate limit")
            return False

        user_limit.requests.append(now)
        return True

    def get_remaining_time(self, user_id: int) -> int:
        user_limit = self._user_limits[user_id]
        if user_limit.blocked_until:
            return int(user_limit.blocked_until - time.time())
        return 0


class ProviderHealthCheck:
    def __init__(self) -> None:
        self._health_status: Dict[str, bool] = {}
        self._last_check: Dict[str, float] = {}
        self._check_interval: float = 60.0

    def mark_unhealthy(self, provider_name: str) -> None:
        self._health_status[provider_name] = False
        self._last_check[provider_name] = time.time()
        logging.warning(f"Provider {provider_name} marcado como não saudável")

    def mark_healthy(self, provider_name: str) -> None:
        self._health_status[provider_name] = True
        self._last_check[provider_name] = time.time()

    def is_healthy(self, provider_name: str) -> bool:
        if provider_name not in self._health_status:
            return True

        if time.time() - self._last_check.get(provider_name, 0) > self._check_interval:
            return True

        return self._health_status.get(provider_name, True)

    def get_status(self) -> Dict[str, bool]:
        return self._health_status.copy()


rate_limiter = RateLimiter()
provider_health = ProviderHealthCheck()
