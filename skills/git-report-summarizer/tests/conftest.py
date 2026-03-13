"""测试路径配置。"""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
ROOT_TEXT = str(ROOT_DIR)
if ROOT_TEXT not in sys.path:
    sys.path.insert(0, ROOT_TEXT)

