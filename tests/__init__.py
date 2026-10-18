import sys
import os

tests_dir = os.path.dirname(__file__)
if tests_dir not in sys.path:
    sys.path.insert(0, tests_dir)

import genlayer
sys.modules["genlayer"] = genlayer
sys.modules["tests.genlayer"] = genlayer
