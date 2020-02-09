import os.path
import sys


def pytest_configure():
    sys.path.insert(0, os.path.abspath("tests/xbmc_mock"))
