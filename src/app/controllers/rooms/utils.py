import random
import string


def generate_room_code() -> str:
    """Generates a UNIQUE 5 character string. [A-Z0-9]"""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
