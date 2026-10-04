from slowapi import Limiter
from slowapi.util import get_remote_address


def client_key(request):
        # Best effort. Behind Render the app only sees Render's internal proxy address, which varies per
    # request, so keying on it never limited anything. Taking the third-from-right X-Forwarded-For
    # entry limits honest clients per real address (verified from two networks), but a client that
    # sends forged proxy headers can still evade it in production. See the README's known limitations.
    xff = request.headers.get("x-forwarded-for", "")
    parts = [p.strip() for p in xff.split(",") if p.strip()]
    if len(parts) >= 3:
        return parts[-3]
    return get_remote_address(request)


limiter = Limiter(key_func=client_key)