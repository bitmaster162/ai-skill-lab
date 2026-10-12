"""Explicit isolated test harness: `python -I -B run_tests.py`."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))  # -I intentionally ignores cwd/PYTHONPATH.
suite = unittest.defaultTestLoader.discover(start_dir=str(ROOT / "tests"),
                                            pattern="test_*.py", top_level_dir=str(ROOT))
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
