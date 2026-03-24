from pathlib import Path
import sys


def _ensure_repo_root_on_path():
    current = Path(__file__).resolve()
    for parent in [current.parent, *current.parents]:
        if (parent / "core").exists():
            path_str = str(parent)
            if path_str not in sys.path:
                sys.path.append(path_str)
            break


_ensure_repo_root_on_path()
