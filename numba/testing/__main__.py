import sys
from . import run_tests

sys.exit(0 if run_tests(sys.argv).wasSuccessful() else 1)
