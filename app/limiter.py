import logging

from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger("uvicorn.error")


def client_key(request):
    # TEMPORARY DIAGNOSTIC: remove after choosing the real key.
    logger.warning(
        "DIAG xff=%r cf=%r tci=%r client=%r",
        request.headers.get("x-forwarded-for"),
        request.headers.get("cf-connecting-ip"),
        request.headers.get("true-client-ip"),
        request.client.host if request.client else None,
    )
    return get_remote_address(request)


limiter = Limiter(key_func=client_key)