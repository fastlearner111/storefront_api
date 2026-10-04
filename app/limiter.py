from slowapi import Limiter
from slowapi.util import get_remote_address


def client_key(request):
    # Behind Render the app only sees Render's internal proxy address, and it varies per request.
    # Clients can write anything they like at the START of X-Forwarded-For, but the proxies append
    # their own entries at the END: the real client address, then Cloudflare, then Render.
    # So the third entry from the right is the one the client cannot forge.
    xff = request.headers.get("x-forwarded-for", "")
    parts = [p.strip() for p in xff.split(",") if p.strip()]
    if len(parts) >= 3:
        return parts[-3]
    return get_remote_address(request)


limiter = Limiter(key_func=client_key)