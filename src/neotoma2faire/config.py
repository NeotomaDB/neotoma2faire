"""Load environment variables from a per-environment ``.env`` file.

The package supports two environments:

* **production** — reads ``.env.production`` from the current working directory.
* **dev**        — reads ``.env.dev`` from the current working directory.

Call :func:`load_env` once, early in ``main()``, before importing modules that
read environment variables at import time (e.g. ``neotoma2faire.api.client``).
"""

from pathlib import Path

from dotenv import load_dotenv


def load_env(use_dev: bool = False) -> Path:
    """Load the appropriate ``.env`` file into ``os.environ``.

    Args:
        use_dev (bool): If ``True``, load ``.env.dev``; otherwise load
            ``.env.production``.

    Returns:
        Path: Absolute path of the file that was attempted. ``load_dotenv``
        silently no-ops when the file does not exist, so callers can use the
        returned path to log / verify which file was picked.
    """
    filename = ".env.dev" if use_dev else ".env.production"
    path = Path.cwd() / filename
    load_dotenv(path, override=True)
    return path
