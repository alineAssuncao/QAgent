from core.middleware import ProviderHealthCheck, RateLimitConfig, RateLimiter


class TestRateLimiter:
    def test_allows_requests_under_limit(self):
        config = RateLimitConfig(max_requests=5, window_seconds=60)
        limiter = RateLimiter(config)

        for _ in range(5):
            assert limiter.is_allowed(12345) is True

    def test_blocks_requests_over_limit(self):
        config = RateLimitConfig(max_requests=3, window_seconds=60)
        limiter = RateLimiter(config)

        for _ in range(3):
            limiter.is_allowed(12345)

        assert limiter.is_allowed(12345) is False

    def test_different_users_independent(self):
        config = RateLimitConfig(max_requests=2, window_seconds=60)
        limiter = RateLimiter(config)

        limiter.is_allowed(111)
        limiter.is_allowed(111)

        assert limiter.is_allowed(222) is True
        assert limiter.is_allowed(111) is False

    def test_returns_remaining_time_when_blocked(self):
        config = RateLimitConfig(max_requests=1, window_seconds=60)
        limiter = RateLimiter(config)

        limiter.is_allowed(12345)
        limiter.is_allowed(12345)

        remaining = limiter.get_remaining_time(12345)
        assert remaining > 0


class TestProviderHealthCheck:
    def test_default_is_healthy(self):
        health = ProviderHealthCheck()
        assert health.is_healthy("Unknown") is True

    def test_mark_unhealthy(self):
        health = ProviderHealthCheck()
        health.mark_unhealthy("TestProvider")
        assert health.is_healthy("TestProvider") is False

    def test_mark_healthy(self):
        health = ProviderHealthCheck()
        health.mark_unhealthy("TestProvider")
        health.mark_healthy("TestProvider")
        assert health.is_healthy("TestProvider") is True

    def test_get_status(self):
        health = ProviderHealthCheck()
        health.mark_unhealthy("Provider1")
        health.mark_healthy("Provider2")

        status = health.get_status()
        assert status["Provider1"] is False
        assert status["Provider2"] is True
