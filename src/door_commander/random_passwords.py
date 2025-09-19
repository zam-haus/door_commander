import base64
import os


# 256bit key by default
def generate_password(bytes=32) -> str:
    return base64.b64encode(os.urandom(bytes)).decode("utf-8")