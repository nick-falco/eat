#!/usr/bin/env python
"""
Script to run all tests in the entire project
"""

import unittest
from sys import exit
from eat.core.tests.test_components import TestTermOperation
from eat.core.tests.test_utilities import TestUtilities
from eat.tests.test_runeat import TestRunEAT


def run_test(class_name):
    suite = unittest.TestLoader().loadTestsFromTestCase(class_name)
    runner = unittest.TextTestRunner(verbosity=3)
    return runner.run(suite)


def main():
    tests = [TestTermOperation, TestUtilities, TestRunEAT]
    passed = True
    for test_class in tests:
        test_result = run_test(test_class)
        if test_result.failures:
            passed = False
    if not passed:
        exit(1)  # One or more test failed
    else:
        exit(0)  # All tests passing


if __name__ == '__main__':
    main()
