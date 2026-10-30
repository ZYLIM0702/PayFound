"""Bounded single-process pilot quotas; no caller identities are logged."""
import hashlib
import os
from .llm import budget, _number


def allowed(kind, identity):
    if os.getenv('PAYFOUND_TESTING') == '1' or os.getenv('DEMO_MODE', 'false').lower() == 'true':
        return True
    setting, default = ('API_PUBLIC_RATE_LIMIT_PER_MINUTE', 600) if kind == 'ip' else ('API_USER_RATE_LIMIT_PER_MINUTE', 120)
    limit = int(_number(setting, default, 1, 100000))
    digest = hashlib.sha256((kind + ':' + identity).encode()).hexdigest()
    return budget.allow('api:' + digest, limit)
