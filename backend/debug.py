from functools import wraps
from flask import abort
from config import debug_status

# Wrapper for routes only available in debug
def debug_only(f):
    @wraps(f)
    def wrapped(**kwargs):
        if not debug_status:
            abort(404)

        return f(**kwargs)

    return wrapped