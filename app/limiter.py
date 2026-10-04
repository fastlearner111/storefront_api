from slowapi import Limiter
from slowapi.util import get_remote_address


def client_key(request):
    
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    return get_remote_address(request)


limiter = Limiter(key_func=client_key)