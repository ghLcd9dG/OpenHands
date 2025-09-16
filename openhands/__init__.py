import os
from pathlib import Path

__package_name__ = 'openhands_ai'


def get_version():
    # Try getting the version from pyproject.toml
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidate_paths = [
            Path(root_dir) / 'pyproject.toml',
            Path(root_dir) / 'openhands' / 'pyproject.toml',
        ]
        for file_path in candidate_paths:
            if file_path.is_file():
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip().startswith('version ='):
                            return line.split('=', 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass

    try:
        from importlib.metadata import PackageNotFoundError, version

        return version(__package_name__)
    except (ImportError, PackageNotFoundError):
        pass

    try:
        from pkg_resources import DistributionNotFound, get_distribution  # type: ignore

        return get_distribution(__package_name__).version
    except (ImportError, DistributionNotFound):
        pass

    return 'unknown'


try:
    __version__ = get_version()
except Exception:
    __version__ = 'unknown'

def __getattr__(name: str):
    if name == 'call_agent':
        from openhands.api import call_agent as _call_agent

        return _call_agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ['__version__', 'get_version', 'call_agent']
