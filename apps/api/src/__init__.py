from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))
