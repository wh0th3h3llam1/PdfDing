# Use dev settings as default, use production if dev settings do not exist
try:
    from .dev import *
except:  # pragma: no cover
    from .prod import *
