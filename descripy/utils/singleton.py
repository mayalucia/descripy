"""There can be only one instance of a singleton."""

class Singleton:
    """
    Base for classes that mayb have only one instance.
    """
    __instance__ = None

    def __new__(cls, *args, **kwargs):
        """..."""
        if cls.__instance__ is None:
            cls.__instance__ = super().__new__(cls, *args, **kwargs)
        return cls.__instance__

    def __init__(self, *args, **kwargs):
        """A single instance can be initialized only once."""
        if self.__class__.__instance__ is None:
            self.__class__.__instance__ = self
            super().__init__(*args, **kwargs)
