"""Utilities to name things."""

import re

def slither(CamelCase):
    """to snake-case
    https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", CamelCase).lower()

def bounce(snake_case):
    """to CamelCase
    https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    return "".join(word.title() for word in snake_case('_'))
