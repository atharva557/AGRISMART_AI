"""Shared placeholder response, replaced by real module behavior later."""


def not_implemented(module):
    return {
        "module": module,
        "error": {
            "code": "NOT_IMPLEMENTED",
            "message": f"The {module} module is not implemented yet.",
        },
    }, 501
