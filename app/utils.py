import bcrypt
#from passlib.context import CryptContext

#if not hasattr(bcrypt, "__about__"):
#    bcrypt.__about__ = type("about", (), {"__version__": bcrypt.__version__})

#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str) -> str:
    
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_pwd.decode('utf-8')

def verify(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)