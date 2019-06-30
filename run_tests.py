#!/usr/bin/env python

import pytest
import os
import yaml
from pyexodiff import exodiff

# Exception class to throw exception for pytest
class pyexodiffException(Exception):
    pass

# Run the current file using pytest
pytest.main(['-v', '-rsx', '--tb=line', 'run_tests.py'])

# Find all 'tests' yml files that contain the test specifications
tests_files = []
for root, dirs, files in os.walk("test/", topdown=False):
    for name in files:
        if name == 'tests':
            tests_files.append(os.path.join(root, name))

# Read yaml data from tests files
tests = {}
for test in tests_files:
    with open(test, 'r') as file:
        testcfg = yaml.safe_load(file)

        # Extract the filepath
        filepath, filename = os.path.split(test)

        for key, values in testcfg.items():
            # Make keys unique by prepending the filepath
            fullpathkey = os.path.join(filepath, key)
            tests[fullpathkey] = values
            tests[fullpathkey]['filepath'] = filepath

            # Add default relative tolerance if not specified in tests file
            if 'rtol' not in key:
                tests[fullpathkey]['rtol'] = 1.0e-6

            # Add default absolute tolerance if not specified in tests file
            if 'atol' not in key:
                tests[fullpathkey]['atol'] = 1.0e-6

# Run all tests found during search
@pytest.mark.parametrize('key', tests)
def test_pyexodiff(key):
    ''' Run all pyexodiff tests using appropriate test function '''

    # If the type key isn't specified, skip test
    if 'type' not in tests[key].keys():
        pytest.skip(key + ': Skipped as test type not specified')

    # If the file key isn't specified, skip test
    if 'file' not in tests[key].keys():
        pytest.skip(key + ': Skipped as file not specified')

    # If the test type is exodiff, run exodiff_test
    if tests[key]['type'] == 'exodiff':
        # If the gold key isn't specified, skip test
        if 'gold' not in tests[key].keys():
            pytest.skip(key + ': Skipped as gold file not specified')
        else:
            exodiff_test(key)

    # If the test type is exception, run the expected_error test
    elif tests[key]['type'] == 'exception':
        # If the expected_error key isn't specified, skip test
        if 'expected_error' not in tests[key].keys():
            pytest.skip(key + ': Skipped as expected_error not specified')
        else:
            with pytest.raises(Exception) as excinfo:
                expected_error(key)

            assert tests[key]['expected_error'] in str(excinfo.value)

    else:
        # Skip unknown test type
        pytest.skip(key + ': Skipped as unknown test type')

    return

def exodiff_test(key):
    ''' Compare Exodus II file with gold file '''

    filepath = tests[key]['filepath']
    filename = tests[key]['file']
    rtol = tests[key]['rtol']
    atol = tests[key]['atol']
    testfilename = os.path.join(filepath, filename)
    gold_filename = os.path.join(filepath, 'gold', tests[key]['gold'])

    try:
        exodiff(testfilename, gold_filename, rtol, atol)

    except:
        with pytest.raises(Exception) as excinfo:
            exodiff(testfilename, gold_filename, rtol, atol)

        assert tests[key]['expected_error'] in str(excinfo.value)

    return

def expected_error(key):
    ''' Raise an exception when an error is thrown while pyexodiff is running '''

    return
