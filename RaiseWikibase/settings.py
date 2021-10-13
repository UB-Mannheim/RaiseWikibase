import json
import os


class Settings(dict):
    """Settings file manager. Provides direct access to attributes and is
    supposed to be used as a context manager."""

    def __init__(self, filename=".config.json"):
        self._filename = filename
        self.load()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.save()
        return False

    def __getattr__(self, key):
        """Forward attribute getter to dictionary."""
        return self[key]

    def __setattr__(self, key, value):
        """Forward attribute setter to dictionary."""
        self[key] = value

    def __eq__(self, other):
        if not isinstance(other, Settings):
            return False
        return self.load() == other.load() and self._filename == other._filename

    def load(self):
        """Try loading settings from file, ignore JSON parsing errors."""
        if os.path.exists(self._filename):
            with open(self._filename, 'r') as f:
                try:
                    self.update(json.load(f))
                except Exception:
                    pass

    def save(self):
        """Save dictionary to file."""
        with open(self._filename, 'w') as f:
            json.dump(dict(
                filter(lambda k: not k[0].startswith('_'), self.items())
            ), f)
